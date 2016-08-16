__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound
from . import super_admin_page, logger
from .check_login import check_login

import app.utils as utils

@super_admin_page.route('/server_core', methods=['GET'])
@check_login
def render_server_core(uid, priv):
    try:
        return render_template('superadmin/server_core.html')
    except TemplateNotFound:
        abort(404)
