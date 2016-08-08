from flask import Flask,current_app
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
socketio = SocketIO(app)
# import blueprints
# to event circular importing, this `import` statement should be put
# after database declared.
from app.blueprints.startup import start_page
from app.blueprints.superadmin import super_admin_page

app.register_blueprint(start_page)
app.register_blueprint(super_admin_page)

# import main views
from app import views
