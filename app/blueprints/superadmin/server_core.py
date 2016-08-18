__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.model.ob_server_core import ServerCORE

from . import super_admin_page, logger
from .check_login import super_admin_only, ajax_super_admin_only

import traceback
import os
from datetime import datetime

rtn = returnModel("string")

# render page
@super_admin_page.route('/server_core', methods=['GET'])
@super_admin_only
def render_server_core_page(uid, priv):
    try:
        return render_template('superadmin/server_core.html',title="hello")
    except TemplateNotFound:
        abort(404)

@super_admin_page.route("/upload_core_file", methods=["POST"])
@ajax_super_admin_only
def upload_core_file(uid, priv):

    def _allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ['jar']

    try:
        gc = GlobalConfig.getInstance()
        F = request.form

        upload_dir = gc.get("files_dir")

        mc_version = F.get("mc_version")
        file_version = F.get("file_version")
        description = F.get("description")
        core_type = F.get("core_type")

        file = request.files['files']

        if file.filename == '':
            return rtn.error(404)

        if file and _allowed_file(file.filename):
            file.save(os.path.join(upload_dir, file.filename))
            # add inst to database
            _file = os.path.join(upload_dir, file.filename)
            
            inst = ServerCORE(
                file_name   = file.filename,
                file_size   = os.path.getsize(_file),
                file_dir    = upload_dir,
                create_time = datetime.now(),
                file_hash   = get_file_hash(_file),
                core_type   = core_type,
                core_version= file_version,
                minecraft_version = mc_version,
                note = description
            )

            db.session.add(inst)
            db.session.commit()

            return rtn.success(200)
        else:
            return rtn.error(411)

    except:
        logger.debug(traceback.format_exc())
        return rtn.error(500)
