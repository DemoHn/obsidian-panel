__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect, send_file
from jinja2 import TemplateNotFound
from urllib.request import urlopen, Request

from app import db, logger
from app.utils import returnModel

from app.tools.mq_proxy import WS_TAG, MessageQueueProxy

from app.model import ServerInstance, ServerCORE, FTPAccount
from app.blueprints.superadmin.check_login import check_login, ajax_check_login
from app.controller.global_config import GlobalConfig

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

proxy = MessageQueueProxy(WS_TAG.APP)
rtn = returnModel("string")

@server_inst_page.route("/dashboard", methods=["GET"])
@check_login
def render_new_dashboard(uid, priv):
    return render_template("/server_inst/index.html")

# miscellaneouses, including basic LOGO, FTP status, server properties, etc.
@server_inst_page.route("/api/get_miscellaneous_info/<inst_id>", methods=["GET"])
@check_login
def render_dashboard_page(uid, priv, inst_id):
    try:
        # get info
        serv_core_obj = db.session.query(ServerInstance).join(ServerCORE).filter(ServerInstance.inst_id == int(inst_id)).first()

        # first, make sure this operation is only allowed by its owner
        if serv_core_obj != None:
            if serv_core_obj.owner_id == uid:
                mc_version = serv_core_obj.ob_server_core.minecraft_version
                # get server properties and motd
                file_server_properties = os.path.join(serv_core_obj.inst_dir,"server.properties")
                motd_string = ""
                server_properties = {}
                if os.path.exists(file_server_properties):
                    parser = KVParser(file_server_properties)
                    server_properties = parser.conf_items
                    motd_string = server_properties.get("motd")

                # LOGO src
                image_source = ""
                inst_dir = serv_core_obj.inst_dir
                logo_file_name = os.path.join(inst_dir, "server-icon.png")
                if os.path.exists(logo_file_name):
                    image_source = "/server_inst/dashboard/logo_src/%s" % inst_id
                # ftp account name
                ftp_account_name = ""
                default_ftp_password = True
                ftp_obj = db.session.query(FTPAccount).filter(FTPAccount.inst_id == inst_id).first()

                if ftp_obj != None:
                    ftp_account_name = ftp_obj.username
                    default_ftp_password = ftp_obj.default_password

                    properties_params = {
                        "motd":motd_string,
                        "image_source": image_source,
                        "mc_version": mc_version,
                        "listen_port": serv_core_obj.listening_port,
                        "ftp_account_name": ftp_account_name,
                        "default_ftp_password": default_ftp_password,
                        "server_properties": server_properties
                    }

                    return rtn.success(properties_params)
                else:
                    return rtn.error(404)
            else:
                return rtn.error(403)
        else:
            return rtn.error(500)

    except TemplateNotFound:
        abort(404)
    except:
        logger.error(traceback.format_exc())
    pass


@server_inst_page.route("/api/get_inst_list", methods=["GET"])
@ajax_check_login
def get_inst_list(uid, priv):
    user_list = {
        "current_id" : None,
        "list": []
    }

    user_insts = db.session.query(ServerInstance).filter(ServerInstance.owner_id == uid).all()
    if user_insts != None:
        if len(user_insts) > 0:
            user_list["current_id"] = user_insts[0].inst_id
            star_flag = False
            for item in user_insts:
                _model = {
                    "inst_name": item.inst_name,
                    "star": item.star,
                    "inst_id": item.inst_id
                }

                user_list["list"].append(_model)
                # get starred instance
                if item.star == True and star_flag == False:
                    user_list["current_id"] = item.inst_id
                    star_flag = True
            return rtn.success(user_list)
        else:
            return rtn.success(user_list)
    else:
        return rtn.success(user_list)

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

# get the external IP address of this server.
# The easiest way is to ask Internet for help!
@server_inst_page.route("/api/get_my_ip", methods=["GET"])
@check_login
def get_my_ip(uid, priv):
    gc = GlobalConfig()
    _url = "http://whatismyip.akamai.com/"

    if gc.get("my_ip_address") == "":
        req = Request(url = _url)
        resp = urlopen(req)

        ip_addr = resp.read().decode()
        # store ip address into cache
        gc.set("my_ip_address", ip_addr)
        return rtn.success(ip_addr)
    else:
        return rtn.success(gc.get("my_ip_address"))

# CONTROL directives
@server_inst_page.route("/api/get_instance_status/<inst_id>", methods=["GET"])
@ajax_check_login
def get_instance_status(uid, priv, inst_id):
    # don't forget to check it
    props = {
        "inst_id" : inst_id
    }
    info = proxy.send("process.get_instance_status", props, WS_TAG.MPW)

    if info == None:
        return rtn.error(500)
    else:
        print(info)
        return rtn.success(info["data"])

@server_inst_page.route("/api/get_instance_log/<inst_id>", methods=["GET"])
@check_login
def get_instance_log(uid, priv, inst_id):
    pass
