__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.model.ob_server_core import ServerCORE

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")

@server_inst_page.route("/ftp", methods=["GET"])
@check_login
def render_ftp_page(uid, priv):
    try:
        return render_template("server_inst/ftp.html",title="FTP")
    except TemplateNotFound:
        abort(404)
