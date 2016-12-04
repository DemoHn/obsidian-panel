__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect, send_file
from jinja2 import TemplateNotFound

from app import db
from app.utils import returnModel

from app.model import ServerInstance
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

from . import server_inst_page
import os

rtn = returnModel("string")

@server_inst_page.route("/dashboard", methods=["GET"])
@check_login
def render_dashboard_page(uid, priv, inst_id = None):
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

                return render_template("server_inst/dashboard.html",
                                       user_list=user_list, current_instance=current_inst_id,
                                       current_instance_name=current_inst_name)
            else:
                # there is no any instance for this user,
                # thus it is better to create another one
                return redirect("server_inst/new_inst")

    except TemplateNotFound:
        abort(404)
    pass


@server_inst_page.route("/dashboard/<inst_id>", methods=["GET"])
@check_login
def render_dashboard_page_II(uid, priv, inst_id):
    try:
        return render_dashboard_page(inst_id=int(inst_id))
    except TemplateNotFound:
        abort(404)

@server_inst_page.route("/dashboard/logo_src/<inst_id>", methods=["GET"])
@check_login
def server_logo_source(uid, priv, inst_id):
    rtn = returnModel("string")
    user_inst_obj = db.session.query(ServerInstance).filter(ServerInstance.inst_id == inst_id).first()
    if user_inst_obj == None:
        # inst id not belong to this user
        abort(403)
    elif user_inst_obj.owner_id != uid:
        abort(403)
    else:
        inst_dir = user_inst_obj.inst_dir
        logo_file_name = os.path.join(inst_dir, "server-icon.png")
        if os.path.exists(logo_file_name):
            return send_file(logo_file_name)
        else:
            abort(404)
