# Graphs for Good ![logo](ui/static/logo_sm.png)

### Helping people help people, one graph at a time

## Background
Our team was present at this year's CapitalOne Digital for Good Hackathon - an annual event that aims to provide tools
and solutions for charities and non-profit organizations to help them grow and succeed in our technology focused society.
By solving problems and removing obstacles for these organizations, they are able to thrive and focus on their core
mission as opposed to being blocked by technological limitations.
After speaking with several charities, we discovered that a common task that they had to perform was data visualization.
Specifically, creating graphs for things like recurring government reports, brochures and marketing materials, and even 
internal tracking and analytics. These groups usually have to manually extract data, use an external tool to create the 
graph, and then repeat this anytime they need to update the graph. It is a time-consuming process that could be accelerated
through the use of an automated pipeline. This is the service we wanted to build to help charities get access to these
graphs when they need them
 
## Introduction

Graphs for Good (G4G) provides a simple service which allows users to register new graphs, define the input data format, and 
then receive these graphs via push email notifications on either a scheduled basis, or anytime the input data changes.

Our service provides a simple, easy to use web interface for registering user accounts, defining new graphs and scheduled
notifications, and viewing existing graphs they have previously defined. Their data is stored in a private S3 repository,
and we expose a REST API endpoint for updating this data at any time. The reason we chose this is that because so many
different charities required a tool like this, instead of limiting the way we source data to a specific database type
or software application, an API endpoint is universally accessible and most systems are extensible enough to set up 
triggers or tasks to push new data to this endpoint.
We monitor this S3 repository for changes to the most recent data. If a graph is registered with a "reactive" schedule, 
anytime new data is pushed to S3 then G4G will instantly generate a new graph and send to to the recipient email(s)
configured to receive them. Otherwise, our scheduling service will generate an email notification according to the
schedule the user defined (daily, weekly, monthly etc.)

Our service runs entirely on AWS lambda functions. We use DynamoDB to store user and graph information, and S3 to store
graph data. Amazon Simple Email Service (SES) is utilized for generating and sending the graph notification emails.
