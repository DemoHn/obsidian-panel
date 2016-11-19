__author__ = "Nigshoxiz"
from flask import render_template, abort, request, redirect
from jinja2 import TemplateNotFound

from app.utils import returnModel
import os
from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login
from app import socketio
from app import db
from app.model import ServerInstance
rtn = returnModel("string")

@server_inst_page.route("/console", methods=["GET"])
@check_login
def render_console_page(uid, priv, inst_id = None):
    try:
        user_list = []
        user_insts_dict = {}
        user_insts = db.session.query(ServerInstance).filter(ServerInstance.owner_id == uid).all()

        if user_insts != None:
            if len(user_insts) > 0:
                current_inst_id = user_insts[0].inst_id
                current_inst_name = user_insts[0].inst_name
                star_flag = False
                for item in user_insts:
                    _model = {
                        "inst_name": item.inst_name,
                        "star": item.star,
                        "inst_id": item.inst_id,
                        "link": "/server_inst/dashboard/" + str(item.inst_id)
                    }
                    user_insts_dict[item.inst_id] = _model
                    user_list.append(_model)
                    # get starred instance
                    if item.star == True and star_flag == True:
                        current_inst_id = item.inst_id
                        current_inst_name = item.inst_name
                        star_flag = True

                # if inst_id is assigned (e.g. GET /dashboard/2)
                if inst_id != None:
                    current_inst_id = inst_id
                    current_inst_name = user_insts_dict[inst_id]["inst_name"]

                return render_template("server_inst/console.html",
                                       user_list=user_list, current_instance=current_inst_id,
                                       current_instance_name=current_inst_name)
            else:
                # there is no any instance for this user,
                # thus it is better to create another one
                return redirect("server_inst/new_inst")

    except TemplateNotFound:
        abort(404)
    pass

@server_inst_page.route("/console/<inst_id>", methods=["GET"])
@check_login
def render_dashboard_page_II(uid, priv, inst_id):
    try:
        return render_console_page(inst_id=int(inst_id))
    except TemplateNotFound:
        abort(404)