__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, app
from app.controller.global_config import GlobalConfig
from app.utils import returnModel
from app.model import Users

from . import super_admin_page, logger
from .check_login import super_admin_only, ajax_super_admin_only
from app.controller.update_check import UpdateChecker

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")
uc  = UpdateChecker()

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
    F = request.json
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

# update software
@super_admin_page.route("/settings/get_current_version", methods=["GET"])
@ajax_super_admin_only
def get_current_version(uid, priv):
    try:
        ver = uc.get_current_version()
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)
    return rtn.success(ver)

@super_admin_page.route("/settings/check_newest_release", methods=["GET"])
@ajax_super_admin_only
def get_newest_version(uid, priv):
    try:
        current_version = uc.get_current_version()
        newest_version = uc.check_newest_release()

        is_newest = True
        if newest_version == None:
            return rtn.error(500)
        else:
            # compare version number
            cur_ver_arr = current_version[1:].split(".")
            new_ver_arr = newest_version["version"][1:].split(".")
            # get array length
            l = 0
            if len(cur_ver_arr) > len(new_ver_arr):
                l = len(cur_ver_arr)
            else:
                l = len(new_ver_arr)
            for i in range(0,l):
                A = -1 # current version frag
                B = -1 # newest version frag
                if i < len(cur_ver_arr):
                    A = int(cur_ver_arr[i])
                if i < len(new_ver_arr):
                    B = int(new_ver_arr[i])

                if B > A:
                    is_newest = False
                    break
                elif B < A:
                    break

            _model = {
                "is_newest" : is_newest,
                "version": newest_version["version"],
                "publish_date": newest_version["publish_date"],
                "release_note": newest_version["release_note"]
            }
            return rtn.success(_model)
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)
    return rtn.success(ver)

@super_admin_page.route("/settings/execute_update", methods=["GET"])
@ajax_super_admin_only
def execute_update(uid, priv):
    try:
        result = uc.update_software()
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)
    return rtn.success(result)

@super_admin_page.route("/settings/reboot", methods=["GET"])
@ajax_super_admin_only
def reboot(uid, priv):
    uc.reboot()
    # In fact, this return line will NEVER be executed since
    # You just restart the whole system!
    return rtn.success(200)
