# Generating Graphs (Using matplotlib)

Deploy using deployment script

Sample event JSON: 
```json
{
  "type": "pie",
  "s3_filename": "/tmp/Frank/data.csv",
  "username": "Frank,
  "labels": ["x", "y", "z"]
}
```

Lambda event common input: 
- type (Must be one of following:)
  * "pie"
  * "line"
  * "bar"
- s3\_filename
- username (To avoid naming conflicts in S3)
- title (optional)

Output one of the following: 
- PNG location on S3 (tmp/usr/<pie/line/bar>.png)
- String 'ERROR' if failed


Each type will trigger a seperate function as defined in the following: 

### generate\_pie()

Unique inputs: 
- labels[] (optional)


### generate\_line()

Unique inputs: 
- x\_column
- y\_column[] (cap to 7, will have run out of colors to plot with)
- xlabel (optional) <defaults to first item in x_column>
- ylabel (optional) <defaults to first item in first y_column>
- x\_constraint (optional) (list, example(\[0,100])



### generate\_bar()

Unique inputs: 
- columns[] (cap to ~20)
- xlabel[] (optional)
- ylabel (optional)

