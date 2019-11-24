# Generating Graphs (Using matplotlib)

### generate\_pie()

Inputs: 
- s3\_filename
- title (optional)
- labels[] (optional)

Output: 
- PNG location on S3 (usr/pie/id)


### generate\_line()

Inputs: 
- s3\_filename
- x\_column
- y\_column[] (cap to ~10)
- title (optional)
- xlabel (optional)
- ylabel (optional)
- x\_constraint (optional)

Output: 
- PNG location on S3 (usr/line/id)



### generate\_bar()

Inputs: 
- s3\_filename
- columns[] (cap to ~20)
- title (optional)
- xlabel[] (optional)
- ylabel (optional)

Output: 
- PNG location on S3 (usr/bar/id)
