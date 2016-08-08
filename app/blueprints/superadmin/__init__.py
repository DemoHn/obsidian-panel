__author__ = "Nigshoxiz"

# import libs
from flask import Blueprint, render_template, abort, request, redirect

from functools import wraps

# import models
from app.model.ob_token import UserToken
# import routes
from . import login

super_admin_page = Blueprint("super_admin_page", __name__,
                             template_folder="templates",
                             url_prefix="/super_admin")

# check if user is login
def check_login(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        # read token
        session_token = request.cookies.get("session_token")
        if session_token == None:
            return redirect("/super_admin/login")
        else:
            user = UserToken.query.filter_by(token=session_token).first()
            if user is None:
                return redirect("/super_admin/login")
            else:
                return fn(*args, **kwargs, _uid = user.uid)

    return decorated_function


