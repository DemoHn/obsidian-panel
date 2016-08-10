__author__ = "Nigshoxiz"

# import libs
from flask import Blueprint

server_inst_page = Blueprint("server_inst_page", __name__,
                             template_folder='templates',
                             url_prefix='/server_inst')

# import routes
from . import views
