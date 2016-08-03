from flask import Flask,current_app
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# shut up, please. I don't wanna see your useless notice again !!
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# close SQLalchemy debug mode
app.config["SQLALCHEMY_ECHO"] = False

# init flask-SQLAlchemy
db = SQLAlchemy(app)

# import blueprints
# to event circular importing, this `import` statement should be put
# after database declared.
from app.blueprints.start import start_page

app.register_blueprint(start_page)
# import main views
from app import views
