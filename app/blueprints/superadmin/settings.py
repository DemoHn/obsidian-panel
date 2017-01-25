__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, app
from app.controller.global_config import GlobalConfig
from app.utils import returnModel
from app.model import Users

from . import super_admin_page, logger
from .check_login import super_admin_only, ajax_super_admin_only

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")

# render page
@super_admin_page.route('/settings', methods=['GET'])
@super_admin_only
def render_settings_page(uid, priv):
    try:
        return render_template('superadmin/index.html')
    except TemplateNotFound:
        abort(404)

# set password
@super_admin_page.route("/settings/passwd", methods=["POST"])
@ajax_super_admin_only
def set_password(uid, priv):
    F = request.form
    ori_password = F.get("ori_password")
    new_password = F.get("new_password")
    try:

        result, _ = Users.compare_password(None, ori_password, uid=uid)
        if result == True:
            Users.set_password(new_password, uid = uid)
            return rtn.success(True)
        else:
            return rtn.error(503)
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)

