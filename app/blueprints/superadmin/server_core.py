__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound
from . import super_admin_page, logger
from .check_login import super_admin_only

from app.controller.global_config import GlobalConfig
import app.utils as utils

# render page
@super_admin_page.route('/server_core', methods=['GET'])
@super_admin_only
def render_server_core_page(uid, priv):
    try:
        return render_template('superadmin/server_core.html')
    except TemplateNotFound:
        abort(404)

# download instance
#@super_admin_page.route()