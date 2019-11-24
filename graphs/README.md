# Generating Graphs (Using matplotlib)

Deploy using deployment script

Sample event JSON: 
{
  "type": "pie",
  "s3\_filename": "/tmp/Frank/data.csv",
  "username": "Frank,
  "labels": \["x", "y", "z"]
}

Lambda event input: 
- type (Must be one of following:)
  * "pie"
  * "line"
  * "bar"
- s3\_filename
- username (To avoid naming conflicts in S3)
- title (optional)

Each type will trigger a seperate function as defined in the following: 
### generate\_pie()

Inputs: 
- labels[] (optional)

Output: 
- PNG location on S3 (tmp/usr/pie.png)


### generate\_line()

Inputs: 
- x\_column
- y\_column[] (cap to ~10)
- xlabel (optional)
- ylabel (optional)
- x\_constraint (optional) (list, example(\[0,100])

Output: 
- PNG location on S3 (tmp/usr/line.png)



### generate\_bar()

Inputs: 
- columns[] (cap to ~20)
- xlabel[] (optional)
- ylabel (optional)

Output: 
- PNG location on S3 (tmp/usr/bar.png)
