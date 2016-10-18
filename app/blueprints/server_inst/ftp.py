__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.model import FTPAccount

from . import server_inst_page, logger
from app.blueprints.superadmin.check_login import check_login

import traceback
import os, json
from datetime import datetime

rtn = returnModel("string")

@server_inst_page.route("/ftp", methods=["GET"])
@check_login
def render_ftp_page(uid, priv):
    try:
        account_name = ""
        ftp_obj = db.session.query(FTPAccount).filter(FTPAccount.owner_id == uid).first()

        if ftp_obj != None:
            account_name = ftp_obj.username
        return render_template("server_inst/ftp.html",
                               title="FTP",ftp_account_name = account_name)
    except TemplateNotFound:
        abort(404)
