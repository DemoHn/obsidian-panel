__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.model import ServerCORE

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")

@server_inst_page.route("/_create_inst", methods=["GET"])
@check_login
def create_new_instance(uid, priv):
    '''
    create a new MC Server instance.
    So How to create a new instance?

    0. Name it.
    1. Select the Server Core File (or upload it by user?)
    2. Select Java Version
    3. Set server.properties
    4. Upload Mods & Plugins (If so)
    5. Go For It!

    :return:
    '''
    try:

        return render_template("server_inst/dashboard.html",title="Dashboard")
    except TemplateNotFound:
        abort(404)