__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

from app import db, app
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.model import ServerCORE

from . import super_admin_page, logger
from .check_login import super_admin_only, ajax_super_admin_only

rtn = returnModel("string")

# render page
@super_admin_page.route('/info', methods=['GET'])
@super_admin_only
def render_info_page(uid, priv):
    try:
        return render_template('superadmin/index.html')
    except TemplateNotFound:
        abort(404)
