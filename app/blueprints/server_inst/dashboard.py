__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.controller.user_inst import InstanceController
from app.utils import returnModel, get_file_hash
from app.model import ServerCORE

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")

@server_inst_page.route("/dashboard", methods=["GET"])
@check_login
def render_dashboard_page(uid, priv):
    try:
        return render_template("server_inst/dashboard.html",title="Dashboard")
    except TemplateNotFound:
        abort(404)

@server_inst_page.route("/boom", methods=["GET"])
@ajax_check_login
def boom(uid, priv):

    try:
        InstanceController.start(1)
        return rtn.success(200)
    except Exception:
        traceback.print_exc()
        return rtn.error(500)