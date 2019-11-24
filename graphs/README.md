# Generating Graphs (Using matplotlib)

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
