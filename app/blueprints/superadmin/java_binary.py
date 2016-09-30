__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.utils import returnModel
from app.model import ServerCORE
from app.tools.mc_downloader.sourceJAVA import sourceJAVA

from . import super_admin_page, logger
from .check_login import super_admin_only

download_queue = []

rtn = returnModel("string")

# render page
@super_admin_page.route('/java_binary', methods=['GET'])
@super_admin_only
def render_java_binary_page(uid, priv):
    try:
        return render_template('superadmin/java_binary.html',title="java binary")
    except TemplateNotFound:
        abort(404)

# TODO TEST
@super_admin_page.route("/java_binary/get_list", method=["GET"])
@super_admin_only
def get_download_list(uid, priv):
    source = sourceJAVA()
    list = source.get_download_list()
    return rtn.success(list)

# TODO TEST
@super_admin_page.route("/java_binary/download", methods=["POST"])
@super_admin_only
def add_download_task(uid, priv):
    '''
    when accessing this route, a new JDK starts downloading in the background.
    Due to the limitation of current technology, we only allow one file to download at the
    same time.
    request params: [POST]
    :major: <major version of java>
    :minor: <minor version of java>
    '''
    try:
        F = request.form
        major_ver = F.get("major")
        minor_ver = F.get("minor")

        source = sourceJAVA()
        link = source.get_download_link(major_ver, minor_ver)

        if link != None:
            download_queue.append(link)
        else:
            return rtn.error(404)
    except:
        return rtn.error(500)

