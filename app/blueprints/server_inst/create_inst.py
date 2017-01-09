__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect, send_file
from hashlib import md5
from jinja2 import TemplateNotFound
import os, json, shutil

from app import db
from app.controller.global_config import GlobalConfig
from app.controller.user_inst import UserInstance
from app.controller.ftp_controller import FTPController
from app.utils import returnModel, generate_random_string
from app.model import JavaBinary, ServerCORE, ServerInstance, FTPAccount, Users

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

import traceback

rtn = returnModel("string")

@server_inst_page.route("/new_inst", methods=["GET"])
@check_login
def render_index_page(uid, priv):
    return render_template("/server_inst/index.html")

@server_inst_page.route("/api/new_inst", methods=["GET"])
@ajax_check_login
def new_Minecraft_instance(uid, priv):
    '''
    create a new MC Server instance.
    So How to create a new instance?

    0. Name it.
    1. Select the Server Core File (or upload it by user?)
    2. Select Java Version
    3. Set server.properties
    4. Upload Mods & Plugins (If necessary)
    5. Go For It!

    :return:
    '''
    try:
        gc = GlobalConfig()
        # get all versions of java
        java_versions = []
        java_versions_obj = db.session.query(JavaBinary).all()

        default_java_binary_id = int(gc.get("default_java_binary_id"))
        for item in java_versions_obj:
            _model = {
                "name" : "1.%s.0_%s" % (item.major_version, item.minor_version),
                "index" : item.id,
                "selected": ""
            }

            if item.id == default_java_binary_id:
                _model['selected'] = "selected"
            java_versions.append(_model)

        # get all info of server core
        server_cores = []
        server_cores_obj = db.session.query(ServerCORE).all()

        for item in server_cores_obj:
            if item.core_version != None and item.core_version != "":
                _name = "%s-%s-%s" % (item.core_type, item.core_version, item.minecraft_version)
            else:
                _name = "%s-%s" % (item.core_type, item.minecraft_version)
            _model = {
                "name" : _name,
                "index" : item.core_id
            }

            server_cores.append(_model)
        # ...and generate an FTP account.
        user_name_obj = db.session.query(Users).filter(Users.id == uid).first()

        _safe_index = 0
        while _safe_index < 30:
            _safe_index += 1
            ftp_user_name = "%s_%s" % (user_name_obj.username, generate_random_string(3))
            if db.session.query(FTPAccount).filter(FTPAccount.username == ftp_user_name).first() == None:
                break

        rtn_model = {
            "java_versions" : java_versions,
            "server_cores" : server_cores,
            "FTP_account_name" : ftp_user_name
        }
        return rtn.success(rtn_model)
    except:
        return rtn.error(500)

@server_inst_page.route("/api/new_inst/assert_input", methods=["GET"])
@ajax_check_login
def assert_input(uid, priv):
    try:
        G = request.args
        type = G.get("type")
        data = G.get("data")
        # port not GLOBALLY conflict
        if type == "port":
            try:
                d = int(data)
            except:
                return rtn.success(False)
            q = db.session.query(ServerInstance).filter(ServerInstance.listening_port == d).first()

            if q == None:
                return rtn.success(True)
            else:
                return rtn.success(False)

        elif type == "inst_name":
            q = db.session.query(ServerInstance).filter(ServerInstance.inst_name == data and ServerInstance.owner_id == uid).first()

            if q == None:
                if data == "" or data == None:
                    return rtn.success(False)
                else:
                    return rtn.success(True)
            else:
                return rtn.success(False)

        elif type == "ftp_account":
            q = db.session.query(FTPAccount).filter(FTPAccount.username == data).first()
            if q == None:
                if data == "" or data == None:
                    return rtn.success(False)
                else:
                    return rtn.success(True)
            else:
                return rtn.success(False)
        elif type == "_all":
            _model = {
                "port" : False,
                "inst_name" : False,
                "ftp_account" : False
            }
            d = data.split(",")
            # port
            p = db.session.query(ServerInstance).filter(ServerInstance.listening_port == int(d[0])).first()
            if p == None:
                _model["port"] = True
            # inst_name
            q = db.session.query(ServerInstance).filter(ServerInstance.inst_name == d[1] and ServerInstance.owner_id == uid).first()
            if q == None:
                _model["inst_name"] = True
            if d[1] == "" or d[1] == None:
                _model["inst_name"] = False
            # ftp_account
            r = db.session.query(FTPAccount).filter(FTPAccount.username == d[2]).first()
            if r == None:
                _model["ftp_account"] = True
            if d[2] == "" or d[2] == None:
                _model["ftp_account"] = False

            return rtn.success(_model)
        else:
            return rtn.error(500)
    except:
        return rtn.error(500)

# upload image
@server_inst_page.route("/upload_logo", methods=["POST"])
@ajax_check_login
def upload_logo(uid, priv):

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ['png','jpeg','jpg']

    rtn = returnModel("string")
    gc = GlobalConfig.getInstance()

    try:
        if 'file' not in request.files:
            return rtn.error(500)

        # get file object
        file = request.files['file']

        if file.filename == "":
            return rtn.error(500)
        if file and allowed_file(file.filename):
            filename = md5(file.filename.encode()+os.urandom(8)).hexdigest()
            file.save(os.path.join(gc.get("uploads_dir"), filename))
            return rtn.success(filename)

        return rtn.error(500)
    except Exception as e:
        logger.error(traceback.format_exc())
        return rtn.error(500)

@server_inst_page.route("/preview_logo/<logo>", methods=["GET"])
@check_login
def preview_server_logo(uid, priv, logo):
    gc = GlobalConfig.getInstance()
    logo_file_name = os.path.join(gc.get("uploads_dir"), logo)

    if os.path.exists(logo_file_name):
        return send_file(logo_file_name)
    else:
        abort(404)

@server_inst_page.route("/api/new_inst", methods=["POST"])
@ajax_check_login
def submit_new_inst(uid, priv):

    def _inst_directory(inst_id):
        '''
        In order to create a new instance, we have to create an individual space to
        store files first.
        :return:
        '''
        gc = GlobalConfig.getInstance()
        servers_dir = gc.get("servers_dir")

        owner = db.session.query(Users).filter(Users.id == uid).first()

        owner_name = owner.username
        dir_name =  "%s_%s" % (owner_name, inst_id)

        logger.debug("[user_inst] dir_name = %s" % dir_name)
        return os.path.join(servers_dir, dir_name)
        pass

    rtn = returnModel("string")
    gc = GlobalConfig.getInstance()
    try:
        F = request.json

        inst_name    = F.get("inst_name")
        core_file_id = F.get("core_file_id")
        java_bin_id  = F.get("java_bin_id")
        listening_port = F.get("listening_port")
        auto_port_dispatch = F.get("auto_port_dispatch")

        # unit: GiB
        max_RAM = F.get("max_RAM")
        max_user = F.get("max_user")

        # json format
        server_properties = F.get("server_properties")

        # logo url
        logo_url = F.get("logo_url")

        # set encoded motd content
        motd     = F.get("motd")

        # FTP account
        FTP_account_name = F.get("ftp_account")
        FTP_default_password = (F.get("ftp_default_password") == "true")
        FTP_password  = F.get("ftp_password")

        i = UserInstance(uid)

        try:
            if auto_port_dispatch:
                i.set_listening_port()
            else:
                i.set_listening_port(listening_port)

            i.set_instance_name(inst_name)
            i.set_java_bin(java_bin_id)
            i.set_allocate_RAM(int(max_RAM)*1024)
            i.set_server_core(core_file_id)
            i.set_max_user(max_user)

            properties_json = json.loads(server_properties)
            properties_json["motd"] = motd
            i.set_instance_properties(properties_json)

            inst_id = i.create_inst()
            # move logo
            if logo_url != None and logo_url != "":
                logo_file_name = os.path.join(gc.get("uploads_dir"), logo_url)
                if os.path.exists(logo_file_name):
                    shutil.move(logo_file_name, os.path.join(_inst_directory(inst_id), "server-icon.png"))
            # create FTP accountx
            ftp_controller = FTPController()

            if not FTP_default_password:
                _ftp_password = FTP_password
            else:
                _ftp_password = None
            ftp_controller.create_account(uid, FTP_account_name, inst_id, ftp_password=_ftp_password)

            return rtn.success(inst_id)
            # return redirect("/server_inst/dashboard/%s" % inst_id)
        except:
            traceback.print_exc()
            return rtn.error(500)
    except Exception as e:
        logger.error(traceback.format_exc())
        return rtn.error(500)
