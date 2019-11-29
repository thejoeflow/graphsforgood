from flask import Flask
from ui import config

webapp = Flask(__name__)
webapp.secret_key = config.secret_key
webapp.config.update(APPLICATION_ROOT='/ui')

# APP ROUTING MODULES - DON"T REMOVE
from ui import login, main, validation, update
