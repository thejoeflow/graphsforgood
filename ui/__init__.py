from flask import Flask
from ui import config

webapp = Flask(__name__)
webapp.secret_key = config.secret_key

# APP ROUTING MODULES - DON"T REMOVE
from ui import login, main, validation, update, graph
