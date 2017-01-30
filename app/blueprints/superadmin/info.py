__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound

import sys, os, distro, platform
from app import db, app
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, get_file_hash
from app.tools.cpuinfo import cpu
from app.model import ServerCORE

from psutil import virtual_memory

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

@super_admin_page.route('/info/get_server_info', methods=['GET'])
@super_admin_only
def get_server_info(uid, priv):
    _model = {
        "cpu" : {
            "vendor" : "",
            "model" : "",
            "cores" : "",
            "freq" : ""
        },
        "OS" : {
            "arch" : "",
            "kernel" : "",
            "name" : "",
            "distro" : ""
        },
        "memory" : ""
    }

    _model["OS"]["name"]   = platform.system()
    memory_GB = virtual_memory().total /1024/1024/1000.0
    _model["memory"] = "%.2f" % memory_GB

    # TODO: add windows support
    if sys.platform.startswith("linux"):
        _cpu_model = {
            "vendor" : cpu.info[0].get("vendor_id"),
            "model" : cpu.info[0].get("model name"),
            "cores" : len(cpu.info),
            "freq" : cpu.info[0].get("cpu MHz")
        }

        _model["cpu"] = _cpu_model
        _model["OS"]["kernel"] = os.popen("uname -mrs").read()[:-1]
        _model["OS"]["distro"] = "%s %s %s" % distro.linux_distribution()
        _model["OS"]["arch"] = platform.machine()
    return rtn.success(_model)
