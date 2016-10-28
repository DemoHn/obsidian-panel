__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect
from jinja2 import TemplateNotFound

from app import db, socketio
from app.controller.global_config import GlobalConfig
from app.tools.mc_downloader import DownloaderPool

from app.utils import returnModel
from app.model import JavaBinary
from app.tools.mc_downloader.sourceJAVA import sourceJAVA

from . import super_admin_page, logger
from .check_login import super_admin_only, ws_super_admin_only

import tarfile
import traceback
from datetime import datetime

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
        return render_template('superadmin/java_binary.html',title="java binary")
    except TemplateNotFound:
        abort(404)

@super_admin_page.route("/java_binary/get_list", methods=["GET"])
@super_admin_only
def get_download_list(uid, priv):

    source = sourceJAVA()
    _list = source.get_download_list()

    dw_list = []
    for item in _list:

        _dw = {
            "progress": 0.0,
            "status": _utils.WAIT,
            "current_hash": ""
        }
        # get status from cache (to return correct data even if the web page refreshed)
        #for _key in download_queue:
        #    q = download_queue.get(_key)
        #    if q.get("link") == item.get("link"):
        #        _dw["progress"] = q.get("progress")
        #        _dw["status"] = q.get("status")
        #        _dw["current_hash"] = _key

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
            "dw" : _dw
        }

        dw_list.append(_model)
    return rtn.success(dw_list)

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

            logger.debug("Download Result: %s" % download_result)
            logger.debug("Start Extracting File...")

            # send extract_start event
            download_queue[hash]["status"] = _utils.EXTRACTING
            _utils.send_dw_signal("_extract_start", hash, True)

            # open archive
            archive = tarfile.open(filename)
            try:
                archive.extractall(path=bin_dir)
            except:
                archive.close()
                download_queue[hash]["status"] = _utils.EXTRACT_FAIL
                # send extract_finish event (when extract failed)
                _utils.send_dw_signal("_extract_finish", hash, False)
                return None

            logger.debug("extract dir: %s, finish!" % bin_dir)
            archive.close()

            try:
                # save the version info into the database
                version_data = JavaBinary(
                    major_version=major_ver,
                    minor_version=minor_ver,
                    bin_directory=bin_dir,
                    install_time=datetime.now()
                )
                db.session.add(version_data)
                db.session.commit()
            except:
                # writing database error
                logger.error(traceback.format_exc())
                download_queue[hash]["status"] = _utils.FAIL
                _utils.send_dw_signal("_download_finish", hash, False)

            download_queue[hash]["status"] = _utils.FINISH
            _utils.send_dw_signal("_extract_finish", hash, True)

        def _send_finish_event(download_result, filename):
            # send finish event
            download_queue[hash]["status"] = _utils.FINISH
            _utils.send_dw_signal("_download_finish", hash, True)

        def _network_error(e):
            download_queue[hash]["status"] = _utils.FAIL
            _utils.send_dw_signal("_download_finish", hash, False)

        dp = DownloaderPool.getInstance()
        inst, hash = dp.newTask(link, download_dir=download_dir)
        # add cookies to download java directly
        inst.disableSSLCert()
        inst.setHeaders({
            "Cookie": "oraclelicense=accept-securebackup-cookie"
        })
        # Since multi thread is not stable here,
        # we decided to use only one thread to download it
        inst.set_force_singlethread(True)
        # global config
        gc = GlobalConfig.getInstance()
        bin_dir = gc.get("lib_bin_dir")

        # add hook
        inst.addDownloadFinishHook(_send_finish_event)
        inst.addDownloadFinishHook(_extract_file)
        inst.addNetworkErrorHook(_network_error)
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
            # create new task and download
            inst, hash = _add_java_task(link, files_dir)
            _utils.queue_add(hash, link)
            download_queue[hash]["status"] = _utils.DOWNLOADING

            return rtn.success(hash)
        else:
            return rtn.error(404)
    except:
        logger.error(traceback.format_exc())
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
    def _parse_msg(msg):
        return msg.get("hash"), msg.get("event"), msg.get("value")

    hash, event, value = _parse_msg(msg)
    dp = DownloaderPool.getInstance()
    if event == "_request_progress":
        _t = dp.get(hash)

        if _t != None:
            inst = _t.dl
            _dw, _filesize = inst.getProgress()

            # update data on download_queue
            if _filesize > 0 and \
                            _dw != None and _filesize != None:
                download_queue[hash]["progress"] = _dw / _filesize

            _utils.send_dw_signal("_get_progress", hash, (_dw, _filesize))