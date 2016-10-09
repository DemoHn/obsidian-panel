__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect
from jinja2 import TemplateNotFound

from app.controller.user_inst import UserInstance
from app.utils import returnModel

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login

import traceback
import os, json
from datetime import datetime

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
        return render_template("server_inst/new_inst.html",title="New instance")
    except TemplateNotFound:
        abort(404)

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
