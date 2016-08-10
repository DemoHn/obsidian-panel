__author__ = "Nigshoxiz"

# import libs
from flask import Blueprint

super_admin_page = Blueprint("super_admin_page", __name__,
                             template_folder="templates",
                             url_prefix="/super_admin")

# import routes
from . import login