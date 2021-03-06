#!/bin/bash

f_name=generate_graph  # lambda function name
src_files=generate_bar.py generate_pie.py generate_line.py generate_graph.py
handler=generate_graph.lambda_handler  # this would be whick file the lambda_handler function is in
using_layer=false  # this would be if using a layer, I don't think anything apart from generate_graph is using it so leave it on false

if [ -f "aws.log" ]; then 
  rm aws.log
fi

if [[ ${using_layer} ]]; then 
  echo "checking for lambda layer"
  layernum=$(aws lambda list-layers | python -c "import sys,json; print(len(json.load(sys.stdin)['Layers']))")

  if [ $layernum -lt 1 ]; then
    echo "  publishing lambda layer, this might take a while..."
    aws lambda publish-layer-version --layer-name matplotlib --zip-file fileb://package.zip  --compatible-runtimes "python3.7" >> aws.log
  else
    echo "  matplotlib layer already exists"
  fi

  echo "  getting lambda layer arn"
  arn="$(aws lambda list-layers | python -c "import sys,json; l=json.load(sys.stdin)['Layers']; n=next((y for y in l if y['LayerName']=='matplotlib'),None); print(n['LatestMatchingVersion']['LayerVersionArn'])")"

fi 
echo "checking for lambda function"
exist="$(aws lambda list-functions | python -c "import sys,json; d=json.load(sys.stdin); n=next((f for f in d['Functions'] if f['FunctionName']=='generate_graph'),None); print('y') if n is not None else print('n')")"

if [ "$exist" == "n" ]; then
  
  echo "  creating lambda function generate_graph"
  echo "    zipping source code"
  if [ -f "function.zip" ]; then
    rm function.zip
  fi
  zip function.zip ${src_files} > /dev/null

  echo "    creating lambda function..."
  if [[ ${using_layer} ]]; then 
    aws lambda create-function --function-name ${f_name} --runtime "python3.7" --handler "generate_graph.lambda_handler" --role arn:aws:iam::868512170571:role/lambda_s3_ses --layers ${arn} --zip-file fileb://function.zip --timeout 10 --memory-size 256 >> aws.log
  else 
    aws lambda create-function --function-name ${f_name} --runtime "python3.7" --handler "${handler}" --role arn:aws:iam::868512170571:role/lambda_s3_ses --zip-file fileb://function.zip --timeout 10 --memory-size 256 >> aws.log
  fi

else
  echo "  lambda function exists, updating code..."
  echo "    zipping source code"
  if [ -f "function.zip" ]; then
    rm function.zip
  fi
  zip function.zip ${src_files} > /dev/null

  echo "    uploading code..."
  aws lambda update-function-code --function-name ${f_name} --zip-file fileb://function.zip >> aws.log

fi

echo "Done. AWS results are in aws.log"
