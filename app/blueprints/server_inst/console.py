__author__ = "Nigshoxiz"
from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import signals, socketio
from app.utils import returnModel

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login

#from app.controller.user_inst import _send_log_sig, _inst_starting_sig
from app.controller.user_inst import InstanceController
from app import app, watcher

rtn = returnModel("string")

@server_inst_page.route("/console", methods=["GET"])
@check_login
def render_console_page(uid, priv):
    try:
        return render_template("server_inst/console.html",title="Console")
    except TemplateNotFound:
        abort(404)

#@_send_log_sig.connect_via(app)
def ws_send(pkg):
    inst_id , data = pkg
    print("wtf")
    socketio.emit("recv",data)

@socketio.on('input')
def input_data(data):
    # TODO
    INST_ID = 1
    inst = watcher.get_instance(INST_ID)
    inst.send_command(data["data"])

