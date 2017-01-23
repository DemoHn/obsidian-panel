__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect
from jinja2 import TemplateNotFound

from app import db, proxy, app
from app.model import JavaBinary
from app.utils import returnModel
from app.tools.mc_downloader import sourceJAVA
from app.tools.mq_proxy import WS_TAG

from . import super_admin_page, logger
from .check_login import super_admin_only, ajax_super_admin_only

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
        ws_port = app.config.get("ws_port")
        return render_template('superadmin/index.html', ws_port = ws_port)
    except TemplateNotFound:
        abort(404)

@super_admin_page.route("/api/get_java_download_list", methods=["GET"])
@ajax_super_admin_only
def get_java_download_list(uid, priv):
    '''
        init a list of all java versions.
        dw_list model:
        {
            "major" : ***,
            "minor" : ***,
            "link" : ***,
            "dw" : {
                "progress",
                "status,
                "current_hash",
            }
        }
        :param flag:
        :param values:
        :return:
        '''
    source = sourceJAVA()
    _list = source.get_download_list()

    dw_list = []
    for item in _list:
        _dw = {
            "progress": 0.0,
            "status": _utils.WAIT,
            "current_hash": ""
        }

        # fetch active download tasks
        _tasks_obj = proxy.send("task.download_pool_status", {}, WS_TAG.TSR)
        _tasks     = _tasks_obj["data"]

        for task in _tasks:
            if _tasks[task]["link"] == item.get("link"):
                _dw["progress"] = _tasks[task]["progress"]
                _dw["status"] = _tasks[task]["status"]
                _dw["current_hash"] = task
                break

        # and fetch from database if there are some versions already installed.
        res = db.session.query(JavaBinary).filter(
            JavaBinary.major_version == str(item.get("major")),
            JavaBinary.minor_version == str(item.get("minor"))
        ).first()
        # that means, this java version has record on the database
        if res != None:
            _dw["status"] = _utils.FINISH

        _model = {
            "major": item.get("major"),
            "minor": item.get("minor"),
            "link": item.get("link"),
            "dw": _dw
        }

        dw_list.append(_model)

    return rtn.success(dw_list)

@super_admin_page.route("/api/start_download_java", methods=["GET"])
@ajax_super_admin_only
def start_download_java(uid, priv):
    G = request.args

    _index = G.get("index")
    source = sourceJAVA()
    _list  = source.get_download_list()

    if _index.isdigit() == False:
        return rtn.error(402)

    _index = int(_index)
    if _index >= len(_list) or _index < 0:
        return rtn.error(402)
    else:
        _v = {
            "download_link" : source.get_download_link(None, None, index=_index),
            "binary_dir" : source.get_binary_directory(None, None, index=_index),
            "major_version" : _list[_index].get("major"),
            "minor_version" : _list[_index].get("minor"),
            "uid" : uid
        }

        _tasks_obj = proxy.send("task.start_download", _v, WS_TAG.TSR, reply=False)

        return rtn.success(200)
