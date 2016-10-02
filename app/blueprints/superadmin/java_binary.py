__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.tools.mc_downloader import DownloaderPool

from app.utils import returnModel
from app.model import ServerCORE
from app.tools.mc_downloader.sourceJAVA import sourceJAVA

from . import super_admin_page, logger
from .check_login import super_admin_only, ws_super_admin_only

import tarfile
import json

# global variables
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

@super_admin_page.route("/java_binary/get_list", methods=["GET"])
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
    def _add_java_task(link, download_dir):
        '''
        add task of downloading java, with hooks.
        :return: (<instance>, <download_hash>)
        '''

        def _extract_file(download_result, filename):
            # for abnormal input parameters(like empty filename), the only thing is to terminate
            # next steps!
            if download_result == False or filename == None:
                return None

            # event model, which is being sent by socketio
            _event_model = {
                "event": "_extract_finish",
                "hash": hash,
                "success": True
            }

            logger.debug("Download Result: %s" % download_result)
            logger.debug("Start Extracting File...")

            # send extract_start event
            _event_model["event"] = "_extract_start"
            _event_model["success"] = True
            socketio.emit("download_event", _event_model, namespace="/dw")

            archive = tarfile.open(filename)
            try:
                archive.extractall(path=bin_dir)
            except:
                archive.close()

                # send extract_finish event (when extract failed)
                _event_model["event"] = "_extract_finish"
                _event_model["success"] = False
                socketio.emit("download_event", _event_model, namespace="/dw")

            logger.debug("extract dir: %s, finish!" % bin_dir)
            archive.close()

            _event_model["event"] = "_extract_finish"
            _event_model["success"] = True
            socketio.emit("download_event", _event_model, namespace="/dw")

        def _send_finish_event(download_result, filename):
            _model = {
                "event": "_download_finish",
                "hash": hash,
                "success": download_result
            }
            logger.debug('<ws> ' + json.dumps(_model))
            socketio.emit("download_event", _model, namespace="/dw")

        dp = DownloaderPool.getInstance()
        inst, hash = dp.newTask(link, download_dir= download_dir)
        # add cookies to download java directly
        inst.disableSSLCert()
        inst.setHeaders({
            "Cookie": "oraclelicense=accept-securebackup-cookie"
        })
        # global config
        gc = GlobalConfig.getInstance()
        bin_dir   = gc.get("lib_bin_dir")

        inst.addDownloadFinishHook(_send_finish_event)
        inst.addDownloadFinishHook(_extract_file)
        dp.start(hash)
        return inst, hash

    try:
        F = request.form
        gc = GlobalConfig.getInstance()
        files_dir = gc.get("files_dir")

        major_ver = F.get("major")
        minor_ver = F.get("minor")

        source = sourceJAVA()
        link = source.get_download_link(major_ver, minor_ver)

        if link != None:
            download_queue.append(link)
            # create new task and download
            inst, hash = _add_java_task(link, files_dir)
            print(hash)
            return rtn.success(hash)
        else:
            return rtn.error(404)
    except:
        return rtn.error(500)

#@super_admin_page.route("/java_binary/")
#@super_admin_only

@socketio.on("download_event", namespace="/dw")
@ws_super_admin_only
def handle_download_event(msg, uid, priv):
    '''
    handle when some download event trigger
    :param msg:
    :return:
    '''
    print(msg)
    pass


