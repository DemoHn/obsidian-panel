__author__ = "Nigshoxiz"

from flask import render_template, abort, request
from jinja2 import TemplateNotFound
from . import super_admin_page

from app.model.ob_user import Users
import logging

logger = logging.getLogger("ob_panel")

@super_admin_page.route("/login", methods=["GET"])
def get_login_page():
    try:
        return render_template("superadmin/login.html", login_error = None)
    except TemplateNotFound:
        abort(404)

@super_admin_page.route("/login", methods=["POST"])
def login():
    try:
        F = request.form
        username = F.get("username")
        password = F.get("password")

        if not Users.search_username(username):
            return render_template("superadmin/login.html",login_error="username_not_found")

        result = Users.compare_password(username, password)

        if result:
            return render_template("superadmin/index.html")
        else:
            return render_template("superadmin/login.html", login_error="login_error")
    except TemplateNotFound:
        abort(404)

