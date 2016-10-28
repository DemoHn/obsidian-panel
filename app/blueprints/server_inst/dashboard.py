__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect
from jinja2 import TemplateNotFound

from app import db, socketio
from app.utils import returnModel

from app.model import ServerInstance
from app.blueprints.superadmin.check_login import check_login

from . import server_inst_page, logger
from process_watcher import SERVER_STATE

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
            return render_template("server_inst/dashboard.html",
                                   title="Dashboard",
                                   inst_id = inst_id)
    except TemplateNotFound:
        abort(404)

# get instance status
@server_inst_page.route("/dashboard/get_status", methods=["POST"])
@check_login
def get_instance_status(uid, priv):
    F = request.form
    inst_id = F.get("inst_id")

    # check if inst is allowed to control
    _inst = db.session.query(ServerInstance) \
        .filter(ServerInstance.inst_id == inst_id).first()

    if _inst == None:
        return rtn.error(500)
    else:
        owner = _inst.owner_id
        if owner != uid:
            return rtn.error(403)
    try:
        # get status
        _status_model = {
            "status" : -1,
            "max_player" : _inst.max_user,
            "current_player" : -1,
            "current_RAM" : -1,
            "max_RAM" : _inst.max_RAM
        }

        # search proc_pool to get some information
        # TODO active instance
        #active_inst = watcher.get_instance(inst_id)
        active_inst = None

        # if active_inst is None, that means there's no active process
        # running in the server, thus status must be 'HALT'
        if active_inst == None:
            _status_model["status"] = SERVER_STATE.HALT
        else:
            _status_model["status"] = active_inst.get_status()
            # TODO
            _status_model["current_player"] = 0 #watcher.just_get(inst_id).get("current_player")
            _status_model["current_RAM"] = 0 #watcher.just_get(inst_id).get("RAM")
        return rtn.success(_status_model)
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)


@server_inst_page.route("/dashboard/start_inst", methods=["POST"])
@check_login
def start_inst(uid, priv):
    F = request.form
    inst_id = F.get("inst_id")

    # check if inst is allowed to control
    _inst = db.session.query(ServerInstance) \
        .filter(ServerInstance.inst_id == inst_id).first()

    if _inst == None:
        return rtn.error(500)
    else:
        owner = _inst.owner_id
        if owner != uid:
            return rtn.error(403)
    try:

        # then start the instance!
        #InstanceController.start(inst_id)
        return rtn.success(inst_id)
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)


@server_inst_page.route("/dashboard/stop_inst", methods=["POST"])
@check_login
def stop_inst(uid, priv):
    F = request.form
    inst_id = F.get("inst_id")

    # check if inst is allowed to control
    _inst = db.session.query(ServerInstance) \
        .filter(ServerInstance.inst_id == inst_id).first()

    if _inst == None:
        return rtn.error(500)
    else:
        owner = _inst.owner_id
        if owner != uid:
            return rtn.error(403)

    try:
        # then start the instance!
        #InstanceController.stop(inst_id)
        return rtn.success(inst_id)
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)
