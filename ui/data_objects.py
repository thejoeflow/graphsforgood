from ui import graph


class User:

    def __init__(self, json_file):
        self.email = json_file.get('email')
        self.first_name = json_file.get('First Name')
        self.last_name = json_file.get('Last Name')
        self.password_hash = json_file.get('password_hash')
        self.salt = json_file.get('salt')
        graphs = []
        for id, data in json_file.get('graph').items():
            graphs.append(Graph.generate_from_dict(id, data))
        self.graphs = graphs


graph_types = {
    "pie": "Pie Graph",
    "bar": "Bar Graph",
    "line": "Line Graph"
}


class Graph:
    def __init__(self, id, name, inp_s3, out_s3, Async, cron, subject, body, receiver_email, config, date):
        self.id = id
        self.name = name
        self.inp_s3 = inp_s3
        self.out_s3 = out_s3
        self.Async = Async
        self.cron = cron
        self.subject = subject
        self.body = body
        self.receiver_email = receiver_email
        self.config = config
        self.date = date

    def get_emails(self):
        return ",".join(self.receiver_email)

    def get_type(self):
        type = self.config.graph_type
        return graph_types[type]

    def get_graph_url(self):
        return graph.get_public_url(self.out_s3)

    @staticmethod
    def generate_from_dict(id, data):
        graph_config = GraphConfig.generate_from_dict(data['config'])
        return Graph(id, data['graph_Name'], data['inp'], data['out'], data['Async'], data['cron'],
                     data['subject'], data['body'], data['receiver_email'], graph_config, data['Date'], )


class GraphConfig:

    def __init__(self, graph_title, graph_type, labels, x_col, x_label, y_col, y_label):
        self.graph_title = graph_title
        self.graph_type = graph_type
        self.labels = labels
        self.x_col = x_col
        self.x_label = x_label
        self.y_col = y_col
        self.y_label = y_label

    @staticmethod
    def generate_from_request(request):
        form = request.form

        graph_type = form['graphType']
        if graph_type == "pie":
            i = 0
        elif graph_type == "bar":
            i = 1
        else:  # line chart
            i = 2

        title = form.getlist('title')[i]
        labels = None

        xCol = form.get('xAxisCol')
        if not_empty(xCol):
            xAxisCol = int(xCol)
        else:
            xAxisCol = None

        yCols = [int(i) for i in form.getlist('yColumns')]
        if i == 1 or i == 2:
            xLabel = form.getlist('xLabel')[i - 1]
            yLabel = form.getlist('yLabel')[i - 1]
        else:
            xLabel = None
            yLabel = None

        return GraphConfig(title, graph_type, labels, xAxisCol, xLabel, yCols, yLabel)

    @staticmethod
    def generate_from_dict(config):
        return GraphConfig(config['graph_title'], config['graph_type'], config['labels'],
                           config['x_col'], config['x_label'], config['y_col'], config['y_label'])


def not_empty(s):
    return s and s.strip()