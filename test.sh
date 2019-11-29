#!/bin/bash  -x
if [[ -z "$1" ]] || [[ "$1" == "help" ]]; then 
  echo "usage: ./test.sh <function-name> <json payload>"
  exit 0
fi

if [[ "$2" = \w*.json ]] || [[ ! -e "$2" ]]; then
  echo "usage: ./test.sh <function-name> <json payload>"
  if [[ "$2" == *.json ]]; then 
    echo "json"
  fi
  if [[ ! -e "$2" ]]; then 
    echo "exist"
  fi
  echo "$([[ ! -e "$2" ]])"

  exit 1
fi

aws lambda invoke --function-name $1 --payload fileb://$2 resp.json
python - <<END
import json
import pprint
with open('resp.json') as j:
  d = json.load(j)
  
if 'stackTrace' in d:
  s = str()
  for l in d['stackTrace']:
    s += l
  print(s)
else:
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(d)

END
