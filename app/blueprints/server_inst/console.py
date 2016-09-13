__author__ = "Nigshoxiz"
import flask
from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound
from flask_socketio import emit
from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.model import ServerCORE

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login

from app.controller.user_inst import InstanceController
import traceback
import os, json
from datetime import datetime
from app import app


rtn = returnModel("string")

@server_inst_page.route("/console", methods=["GET"])
@check_login
def render_console_page(uid, priv):
    try:
        return render_template("server_inst/console.html",title="Console")
    except TemplateNotFound:
        abort(404)
