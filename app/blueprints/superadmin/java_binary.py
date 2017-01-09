__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect
from jinja2 import TemplateNotFound
from app.utils import returnModel
from . import super_admin_page, logger
from .check_login import super_admin_only, ws_super_admin_only

rtn = returnModel("string")

# some dirty but useful functions' collection
class _utils:

    WAIT = 1
    DOWNLOADING = 2
    EXTRACTING = 3
    FINISH = 4
    FAIL = 5
    EXTRACT_FAIL= 6

# render page
@super_admin_page.route('/java_binary', methods=['GET'])
@super_admin_only
def render_java_binary_page(uid, priv):
    try:
        return render_template('superadmin/index.html')
    except TemplateNotFound:
        abort(404)

