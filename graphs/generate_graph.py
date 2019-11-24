from generate_pie import generate_pie
from generate_line import generate_line
from generate_bar import generate_bar


def lambda_handler(event, context):
    if 'type' in event:
        if event['type'] == 'pie':
            return generate_pie(event)
        elif event['type'] == 'line':
            return generate_line(event)
        elif event['type'] == 'bar':
            return generate_bar(event)
        else:
            print("ERROR - Invalid graph type!")
            return 'ERROR'
    else:
        print("ERROR - Must specify type")
        return 'ERROR'
