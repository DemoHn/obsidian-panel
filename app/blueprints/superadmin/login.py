__author__ = "Nigshoxiz"

from flask import render_template, abort, request
from jinja2 import TemplateNotFound
from . import super_admin_page

from app.model.ob_user import Users

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

        
    except TemplateNotFound:
        abort(404)

