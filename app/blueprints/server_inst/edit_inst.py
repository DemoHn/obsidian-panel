__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect, send_file
import os, json, shutil, traceback

from app import db, app
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, generate_random_string
from app.model import JavaBinary, ServerCORE, ServerInstance, FTPAccount, Users

from . import server_inst_page, logger, version
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

rtn = returnModel("string")

@server_inst_page.route("/edit_inst/<inst_id>", methods=["GET"])
@check_login
def render_edit_index_page(uid, priv, inst_id):
    return render_template("/server_inst/index.html", new_inst_page=0, version = version)
