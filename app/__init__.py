import os, yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.controller.global_config import GlobalConfig
from app.tools.mq_proxy import WS_TAG, MessageQueueProxy

from ob_logger import Logger
logger = Logger("APP", debug=True)

app = Flask(__name__)

# shut up, please. I don't wanna see your useless notice again !!
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# close SQLalchemy debug mode
app.config["SQLALCHEMY_ECHO"] = False
app.config['SECRET_KEY'] = 'secret!'
app.config['REDIS_QUEUE_KEY'] = 'reboot_queue'

gc = GlobalConfig.getInstance()
# set sqlalchemy database uri
if gc.get("database_uri") != None:
    app.config["SQLALCHEMY_DATABASE_URI"] = gc.get("database_uri")

# init flask-SQLAlchemy
db = SQLAlchemy(app)

# read config.yaml directly
zmq_port = int(yaml.load(open("config.yaml","r")).get("broker").get("listen_port"))
proxy = MessageQueueProxy(WS_TAG.APP ,router_port=zmq_port)


# import blueprints
# to event circular importing, this `import` statement should be put
# after database declared.
from app.blueprints.startup import start_page
from app.blueprints.superadmin import super_admin_page
from app.blueprints.server_inst import server_inst_page

# register blueprints
app.register_blueprint(start_page)
app.register_blueprint(super_admin_page)
app.register_blueprint(server_inst_page)

# import main views
from app import views
