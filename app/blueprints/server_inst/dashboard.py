__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect, send_file
from jinja2 import TemplateNotFound

from app import db, logger
from app.utils import returnModel

from app.model import ServerInstance, ServerCORE, FTPAccount
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

from . import server_inst_page
import os, re, traceback

# copied from process_watcher/parser.py
class KVParser(object):
    """
    A general Key-Value Parser
    Parsed File Format :

    # here is comment
    server-ip=12.23.43.3
    motd=This is a Minecraft Server # inline comment

    """
    def __init__(self,file):
        """
        :param file: filename being parsed.
        """
        self.conf_items = {}
        self.file = file
        self.loads()

    def loads(self):
        """
        read the whole config file and make config index
        :return:
        """
        fd = open(os.path.normpath(self.file),"r+")

        if fd == None:
            raise FileNotFoundError
        for line in fd.readlines():
            if line.find("#") == 0:
                continue
            else:
                pattern = "^([a-zA-Z\-_ ]+)=([^#]*)"
                result  = re.match(pattern,line)
                if result != None:
                    key = result.group(1)
                    val = result.group(2).strip()
                    self.conf_items[key] = val
        fd.close()


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
                serv_core_obj = db.session.query(ServerInstance).join(ServerCORE).filter(ServerInstance.inst_id == int(current_inst_id)).first()
                mc_version = serv_core_obj.ob_server_core.minecraft_version
                # get server properties and motd
                file_server_properties = os.path.join(current_inst_obj.inst_dir,"server.properties")
                motd_string = ""
                server_properties = {}
                if os.path.exists(file_server_properties):
                    parser = KVParser(file_server_properties)
                    server_properties = parser.conf_items
                    motd_string = server_properties.get("motd")

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
                                       default_ftp_password = default_ftp_password,
                                       server_properties = server_properties
                )
            else:
                # there is no any instance for this user,
                # thus it is better to create another one
                return redirect("server_inst/new_inst")

    except TemplateNotFound:
        abort(404)
    except:
        logger.error(traceback.format_exc())
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
