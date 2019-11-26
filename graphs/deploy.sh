#!/bin/bash

echo "checking for lambda layer"
layernum=$(aws lambda list-layers | python -c "import sys,json; print(len(json.load(sys.stdin)['Layers']))")

if [ $layernum -lt 1 ]; then
  echo "publishing lambda layer"
  aws lambda publish-layer-version --layer-name matplotlib --zip-file fileb://package.zip  --compatible-runtimes "python3.7"
else
  echo "matplotlib layer already exists, skipping..."
fi

echo "zipping source code"
if [ -f "function.zip" ]; then
  rm function.zip
fi
zip function.zip generate_graph.py generate_pie.py generate_bar.py generate_line.py > /dev/null

# assuming this is the only lambda layer
echo "getting lambda layer arn"
arn="$(aws lambda list-layers | python -c "import sys,json; print(json.load(sys.stdin)['Layers'][0]['LatestMatchingVersion']['LayerVersionArn'])")"

echo "updating function code"
aws lambda update-function-code --function-name generate_graph --zip-file fileb://function.zip > aws.log
rm function.zip

echo "updating function to use layer"
aws lambda update-function-configuration --function-name generate_graph --layers ${arn} --timeout 10 --memory-size 256 --runtime python3.7 >> aws.log

echo "Done. AWS results are in aws.log"
