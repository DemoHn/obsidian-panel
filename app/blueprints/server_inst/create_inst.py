__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect
from jinja2 import TemplateNotFound

from app import db
from app.controller.user_inst import UserInstance
from app.utils import returnModel
from app.model import JavaBinary, ServerCORE, ServerInstance, FTPAccount

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

import traceback


rtn = returnModel("string")

@server_inst_page.route("/new_inst", methods=["GET"])
@check_login
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
        # get all versions of java
        java_versions = {}
        java_versions_obj = db.session.query(JavaBinary).all()
        for item in java_versions_obj:
            java_versions[item.id] = "1.%s.0_%s" % (item.major_version, item.minor_version)

        # get all info of server core
        server_cores = {}
        server_cores_obj = db.session.query(ServerCORE).all()

        for item in server_cores_obj:
            if item.core_version != None and item.core_version != "":
                server_cores[item.core_id] = "%s-%s-%s" % (item.core_type, item.core_version, item.minecraft_version)
            else:
                server_cores[item.core_id] = "%s-%s" % (item.core_type, item.minecraft_version)

        return render_template("server_inst/new_inst.html",java_versions = java_versions, server_cores = server_cores)
    except TemplateNotFound:
        abort(404)

@server_inst_page.route("/new_inst/assert_input", methods=["GET"])
@ajax_check_login
def assert_input(uid, priv):
    rtn = returnModel("string")
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
                return rtn.success(True)
            else:
                return rtn.success(False)

        elif type == "ftp_account":
            q = db.session.query(FTPAccount).filter(FTPAccount.username == data).first()
            if q == None:
                return rtn.success(True)
            else:
                return rtn.success(False)
        else:
            return rtn.error(500)
    except:
        abort(500)


@server_inst_page.route("/new_inst", methods=["POST"])
@check_login
def submit_new_inst(uid, priv):
    try:
        F = request.form

        inst_name    = F.get("inst_name")
        core_file_id = F.get("core_file_id")
        java_bin_id  = F.get("java_bin_id")
        listening_port = F.get("listening_port")
        auto_port_dispatch = F.get("auto_port_dispatch")
        max_RAM = F.get("max_RAM")
        max_user = F.get("max_user")

        # json format
        properties = F.get("server_properties")

        i = UserInstance(uid)

        try:
            if auto_port_dispatch:
                i.set_listening_port()
            else:
                i.set_listening_port(listening_port)

            i.set_instance_name(inst_name)
            i.set_java_bin(java_bin_id)
            i.set_allocate_RAM(max_RAM)
            i.set_server_core(core_file_id)
            i.set_max_user(max_user)

            inst_id = i.create_inst()
            return redirect("/server_inst/dashboard/%s" % inst_id)
        except:
            traceback.print_exc()
            abort(502)
    except Exception as e:
        logger.error(traceback.format_exc())
        abort(500)
