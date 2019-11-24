# Generating Graphs (Using matplotlib)

Sample event JSON: 
{
  type: pie,
  s3\_filename: /tmp/Frank/data.csv,
  username: Frank,
  labels: \[x, y, z]
}

Lambda event input: 
- type (Must be one of following:)
  * 'pie'
  * 'line'
  * 'bar'

Each type will trigger a seperate function as defined in the following: 

### generate\_pie()

Inputs: 
- s3\_filename
- username (To avoid naming conflicts in S3)
- title (optional)
- labels[] (optional)

Output: 
- PNG location on S3 (tmp/usr/pie.png)


### generate\_line()

Inputs: 
- s3\_filename
- username (To avoid naming conflicts in S3)
- x\_column
- y\_column[] (cap to ~10)
- title (optional)
- xlabel (optional)
- ylabel (optional)
- x\_constraint (optional)

Output: 
- PNG location on S3 (tmp/usr/line.png)



### generate\_bar()

Inputs: 
- s3\_filename
- username (To avoid naming conflicts in S3)
- columns[] (cap to ~20)
- title (optional)
- xlabel[] (optional)
- ylabel (optional)

Output: 
- PNG location on S3 (tmp/usr/bar.png)
