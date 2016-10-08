__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.user_inst import InstanceController
from app.utils import returnModel
from app.model import ServerCORE, ServerInstance

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")

@server_inst_page.route("/dashboard", methods=["GET"])
@check_login
def render_inst_selection_page(uid, priv):
    try:
        user_list = []

        user_insts = db.session.query(ServerInstance)\
            .filter(ServerInstance.owner_id == uid).all()

        if user_insts != None:
            for item in user_insts:
                _model = {
                    "inst_name" : item.inst_name,
                    "current_user" : 0, # TODO
                    "total_user" : item.max_user,
                    "status" : "WORK", # TODO
                    "inst_id" : item.inst_id
                }
                user_list.append(_model)

        return render_template("server_inst/inst_select.html",
                               title="Select",
                               user_list = user_list)
    except TemplateNotFound:
        abort(404)
    pass

@server_inst_page.route("/dashboard/<inst_id>", methods=["GET"])
@check_login
def render_dashboard_page(uid, priv, inst_id):
    try:
        inst_data = db.session.query(ServerInstance)\
            .filter(ServerInstance.inst_id == inst_id).first()

        if inst_data == None:
            abort(500)
        else:
            return render_template("server_inst/dashboard.html",title="Dashboard")
    except TemplateNotFound:
        abort(404)

@server_inst_page.route("/dashboard/start_inst", methods=["POST"])
@check_login
def start_inst(uid, priv, inst_id):
    pass

@server_inst_page.route("/dashboard/stop_inst", methods=["POST"])
@check_login
def stop_inst(uid, priv, inst_id):
    pass

# TODO
@server_inst_page.route("/dashboard/restart_inst", methods=["POST"])
def restart_inst(uid, priv, inst_id):
    pass

'''
@server_inst_page.route("/boom", methods=["GET"])
@ajax_check_login
def boom(uid, priv):

    try:
        InstanceController.start(1)
        return rtn.success(200)
    except Exception:
        traceback.print_exc()
        return rtn.error(500)
'''