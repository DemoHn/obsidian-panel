from flask import Flask,current_app
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app)

# import blueprints
# to event circular importing, this `import` statement should be put
# after database declared.
from app.blueprints.start import start_page

app.register_blueprint(start_page)

from app import views
