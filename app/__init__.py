from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

app = Flask(__name__)

# shut up, please. I don't wanna see your useless notice again !!
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# close SQLalchemy debug mode
app.config["SQLALCHEMY_ECHO"] = False
app.config['SECRET_KEY'] = 'secret!'

# init flask-SQLAlchemy
db = SQLAlchemy(app)

# monkey patch eventlet
import eventlet
eventlet.monkey_patch()
# init socketio
socketio = SocketIO(app, message_queue='redis://')

# run process watcher
# in addtion, MPW is 'Minecraft Process Watcher'
from mpw.watchdog import Watchdog
watcher = Watchdog.getWDInstance()

#from ftm import FTPManager
#ftp_manager = FTPManager(2121)

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
