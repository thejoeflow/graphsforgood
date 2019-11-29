from enum import Enum

from flask import request, render_template, session, redirect, url_for

from ui import webapp

@webapp.route('/')
def index():
    return redirect(url_for("main")) if 'email' in session else redirect(url_for("login_register"))


@webapp.route('/main')
def main():
    user_id = 123456
    graphs = get_graphs_for_user(user_id)
    return render_template("/main.html", graphs=graphs)


@webapp.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

def get_graphs_for_user(user_id):
    # TODO: Get user graphs from database
    graphs = [GraphView("abc123", "Monthly Spending", GraphType.PIE, ["test@email.com"], "every day"),
              GraphView("abcd1233", "Favourite Fruits", GraphType.LINE_CHART, ["test@email.com", "admin@systen.com"],
                    "every month"),
              GraphView("jkdfsb3783", "Network Bandwidth - December", GraphType.BAR_CHART, ["user@domain.ca"],
                    "On Data Change")]
    return graphs

class GraphView:

    def __init__(self, id, name, type, subscribers, schedule):
        """
        Instantiates a new graph object
        :param id:
        :param type:
        :param subscribers:
        :param schedule:
        """
        self.id = id
        self.name = name
        self.type = type
        self.subscribers = subscribers
        self.schedule = schedule

    def get_emails(self):
        return ",".join(self.subscribers)

class GraphType(Enum):
    PIE = 1
    LINE_CHART = 2
    BAR_CHART = 3