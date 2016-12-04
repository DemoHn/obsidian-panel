__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect, send_file
from jinja2 import TemplateNotFound

from app import db
from app.utils import returnModel

from app.model import ServerInstance, ServerCORE, FTPAccount
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
                current_inst_obj  = user_insts[0]
                star_flag = False
                for item in user_insts:
                    _model = {
                        "inst_name": item.inst_name,
                        "star": item.star,
                        "inst_id": item.inst_id,
                        "obj" : item,
                        "link": "/server_inst/dashboard/" + str(item.inst_id)
                    }
                    user_insts_dict[item.inst_id] = _model
                    user_list.append(_model)
                    # get starred instance
                    if item.star == True and star_flag == True:
                        current_inst_id = item.inst_id
                        current_inst_name = item.inst_name
                        current_inst_obj = item
                        star_flag = True

                # if inst_id is assigned (e.g. GET /dashboard/2)
                if inst_id != None:
                    current_inst_id = inst_id
                    current_inst_name = user_insts_dict[inst_id]["inst_name"]
                    current_inst_obj  = user_insts_dict[inst_id]["obj"]

                # get info
                serv_core_obj = db.session.query(ServerInstance).join(ServerCORE).filter(ServerInstance.inst_id == current_inst_id).first()

                mc_version = serv_core_obj.ob_server_core.minecraft_version

                # get motd
                file_server_properties = os.path.join(current_inst_obj.inst_dir,"server.properties")
                motd_string = ""
                if os.path.exists(file_server_properties):
                    f = open(file_server_properties, "r")
                    for item in f.readlines():
                        if item.find("motd=") >= 0:
                            motd_string = item[5:]
                            break

                # ftp account name
                ftp_account_name = ""
                default_ftp_password = True
                ftp_obj = db.session.query(FTPAccount).filter(FTPAccount.inst_id == current_inst_id).first()

                if ftp_obj != None:
                    ftp_account_name = ftp_obj.username
                    default_ftp_password = ftp_obj.default_password
                return render_template("server_inst/dashboard.html",
                                       user_list=user_list, current_instance=current_inst_id,
                                       current_instance_name=current_inst_name,
                                       image_source="/server_inst/dashboard/logo_src/%s" % inst_id,
                                       motd = motd_string,
                                       str_ip_port = "127.0.0.1:%s" % current_inst_obj.listening_port,
                                       mc_version = mc_version,
                                       ftp_account_name = ftp_account_name,
                                       default_ftp_password = default_ftp_password
                )
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
