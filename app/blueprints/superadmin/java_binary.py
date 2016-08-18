__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.model.ob_server_core import ServerCORE

from . import super_admin_page, logger
from .check_login import super_admin_only, ajax_super_admin_only

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")

# render page
@super_admin_page.route('/java_binary', methods=['GET'])
@super_admin_only
def render_java_binary_page(uid, priv):
    try:
        return render_template('superadmin/java_binary.html',title="java binary")
    except TemplateNotFound:
        abort(404)
