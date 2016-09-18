__author__ = "Nigshoxiz"
from flask import render_template, abort, request
from jinja2 import TemplateNotFound

from app import signals, socketio
from app.utils import returnModel

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login

#from app.controller.user_inst import _send_log_sig, _inst_starting_sig
from app.controller.user_inst import InstanceController
from app import app, watcher
from flask_socketio import emit, send

rtn = returnModel("string")

@server_inst_page.route("/console", methods=["GET"])
@check_login
def render_console_page(uid, priv):
    try:
        return render_template("server_inst/console.html",title="Console")
    except TemplateNotFound:
        abort(404)
