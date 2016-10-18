__author__ = "Nigshoxiz"
from flask import render_template, abort, request
from jinja2 import TemplateNotFound

from app.utils import returnModel
import os
from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login
from app import socketio
rtn = returnModel("string")

@server_inst_page.route("/console", methods=["GET"])
@check_login
def render_console_page(uid, priv):
    try:
        return render_template("server_inst/console.html",title="Console")
    except TemplateNotFound:
        abort(404)