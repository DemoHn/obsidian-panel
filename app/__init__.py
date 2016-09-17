from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from blinker import Namespace

app = Flask(__name__)

# shut up, please. I don't wanna see your useless notice again !!
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# close SQLalchemy debug mode
app.config["SQLALCHEMY_ECHO"] = False
app.config['SECRET_KEY'] = 'secret!'

# init flask-SQLAlchemy
db = SQLAlchemy(app)

# init socketio
socketio = SocketIO(app, message_queue='redis://')

# init signals
signals = Namespace()

# run process watcher
# in addtion, MPW is 'Minecraft Process Watcher'
from mpw import Watchdog
from app.controller.inst_events import InstanceEventEmitter

watcher = Watchdog.getWDInstance()
watcher.launch(hook_class=InstanceEventEmitter)
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
