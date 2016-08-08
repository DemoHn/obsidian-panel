__author__ = "Nigshoxiz"

from flask import render_template, abort
from jinja2 import TemplateNotFound
from . import super_admin_page
from .check_login import check_login

@super_admin_page.route("/login", methods=["GET"])
def login():
    try:
        return render_template("superadmin/login.html", login_error = None)
    except TemplateNotFound:
        abort(404)

