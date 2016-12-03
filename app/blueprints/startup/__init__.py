__author__ = "Nigshoxiz"

# import models
from flask import Blueprint, render_template, abort, request, make_response
from flask_socketio import send, emit
from jinja2 import TemplateNotFound
from app import socketio
from app.utils import returnModel, salt

import hashlib
import traceback
import logging
import tarfile
import json
import subprocess
import time
from functools import wraps
# import controllers
from app.controller.config_env import DatabaseEnv, JavaEnv
from app.controller.init_main_db import init_database, migrate_superadmin
from app.controller.global_config import GlobalConfig
from app.controller.sys_process import SystemProcessClient
from app.tools.mc_downloader import  DownloaderPool

start_page = Blueprint("start_page", __name__,
                       template_folder='templates',
                       url_prefix="/startup")

# filter requests after start-up settings has been done.
def only_on_startup(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        gc = GlobalConfig.getInstance()
        if gc.get("init_super_admin") == True:
            return abort(403)
        else:
            return fn(*args, **kwargs)
    return decorated_function

@start_page.route("/", methods=["GET"])
@only_on_startup
def show_starter_page():
    try:
        _step = request.args.get("step")

        if _step == None:
            _step = 1
        _step = int(_step)

        if _step == 1:
            return render_template("startup/startup_super_admin.html")
        elif _step == 2:
            return render_template("startup/startup_source_java.html")
        elif _step == 3:
            return render_template("startup/startup_database.html", g_error_hidden="none")
        else:
            abort(404)
    except TemplateNotFound:
        abort(404)

@start_page.route("/", methods=["POST"])
@only_on_startup
def handle_init_config():
    logger = logging.getLogger("ob_panel")
    try:
        F = request.form
        _step = request.args.get('step')
        _step = int(_step)
        if _step == 2:
            email = F.get("email")
            username = F.get("username")
            password = F.get("password")

            try:
                # NOTICE: At the beginning, wejava_executable use temperate sqlite database to store superadmin's
                # username and password. Then after initialization, just migrate them to the formal
                # database.
                gc = GlobalConfig.getInstance()
                gc.set("temp_superadmin_username", username)
                gc.set("temp_superadmin_email", email)
                gc.set("temp_superadmin_hash", hashlib.md5(password.encode('utf-8')+salt).hexdigest())
            except:
                logger.error(traceback.format_exc())
                return abort(500)

            return render_template("startup/startup_source_java.html")
        elif _step == 3:
            try:
                gc = GlobalConfig.getInstance()
                #gc.set("")
            except:
                logger.error(traceback.format_exc())
                return abort(500)
            return render_template("startup/startup_database.html", g_error_hidden="none")
        else:
            abort(404)
    except TemplateNotFound:
        abort(404)


@start_page.route("/finish", methods=["POST"])
@only_on_startup
def starter_finish():
    try:
        logger = logging.getLogger("ob_panel")
        F = request.form
        gc = GlobalConfig.getInstance()
        db = DatabaseEnv()

        db_env = F.get("db_env")

        if db_env == "sqlite":
            db.setDatabaseType("sqlite")
            # set init flag = True
            gc.set("init_super_admin", "True")
            # then init database
            init_database()
            migrate_superadmin()
            gc.set("_RESTART_LOCK", "True")
            return render_template("startup/finish.html")
        elif db_env == "mysql":
            db.setDatabaseType("mysql")

            _u = F.get("mysql_username")
            _p = F.get("mysql_password")

            if db.testMySQLdb(_u,_p) == True:
                gc.set("init_super_admin","True")

                db.setMySQLinfo(_u, _p)
                init_database()
                migrate_superadmin()
                gc.set("_RESTART_LOCK", "True")
                return render_template("startup/finish.html")
            else:
                return render_template("startup/startup_database.html", g_error_hidden="block")

    except TemplateNotFound:
        abort(404)

@start_page.route("/__reboot", methods=["GET"])
def __reboot_once():
    gc = GlobalConfig.getInstance()

    if gc.get("_RESTART_LOCK") == True:
        gc.set("_RESTART_LOCK", "False")
        _restart_process()
    #return response
# ajax data
#
# in step=2 (detect Java Environment)
#
# NOTE : this route (and the following 'download java' route) is somehow dangerous since anyone has privilege
# to operate. Thus, it's better to warn users to finish the starter steps as soon as possible.
@start_page.route("/detect_java_environment")
@only_on_startup
def detect_java_environment():
    rtn = returnModel("string")
    gc  = GlobalConfig.getInstance()

    try:
        env = JavaEnv()
        java_envs = []
        __dir, __ver = env.findSystemJavaInfo()
        if __dir != None:
            _model = {
                "name" : "java",
                "dir" : "(%s)" % __dir
            }
            java_envs.append(_model)

        _arr = env.findUserJavaInfo()
        for java_ver in _arr:
            _model = {
                "name" : "JDK %s" % java_ver['version'],
                "dir" : "(%s)" % java_ver["dir"]
            }

            java_envs.append(_model)
        return rtn.success(java_envs)
        #return rtn.success([])
    except:
        return rtn.error(500)
    pass

@start_page.route("/download_java")
@only_on_startup
def download_java():
    #socketio.emit("download_event",{"dat":42})
    def _extract_file(download_result, filename):
        _event_model = {
            "event": "_extract_finish",
            "hash": _hash,
            "success": True
        }

        logger.debug("Download Result: %s" % download_result)
        logger.debug("Start Extracting File...")

        # send extract_start event
        _event_model["event"] = "_extract_start"
        _event_model["success"] = True
        socketio.emit("download_event", _event_model)

        archive = tarfile.open(filename)
        try:
            archive.extractall(path=bin_dir)
        except:
            archive.close()

            # send extract_finish event (when extract failed)
            _event_model["event"] = "_extract_finish"
            _event_model["success"] = False
            socketio.emit("download_event", _event_model)

        logger.debug("extract dir: %s, finish!" % bin_dir)
        archive.close()

        _event_model["event"] = "_extract_finish"
        _event_model["success"] = True
        socketio.emit("download_event", _event_model)

    def _send_finish_event(download_result, filename):
        _model = {
            "event": "_finish",
            "hash": _hash,
            "success": download_result
        }
        logger.debug('<ws> ' + json.dumps(_model))
        socketio.emit("download_event", _model)

    logger = logging.getLogger("ob_panel")
    rtn = returnModel("string")
    gc  = GlobalConfig.getInstance()

    bin_dir   = gc.get("lib_bin_dir")
    files_dir = gc.get("files_dir")

    # TODO only jdk 8u102?
    java_url = "http://download.oracle.com/otn-pub/java/jdk/8u102-b14/jdk-8u102-linux-x64.tar.gz"
    #java_url = "http://mirrors.zju.edu.cn/debian/indices/Maintainers"
    try:
        dp = DownloaderPool.getInstance()
        inst,_hash = dp.newTask(java_url, download_dir=files_dir)

        inst.disableSSLCert()
        inst.setHeaders({
            "Cookie": "oraclelicense=accept-securebackup-cookie"
        })

        inst.addDownloadFinishHook(_send_finish_event)
        inst.addDownloadFinishHook(_extract_file)
        dp.start(_hash)
        return rtn.success(_hash)
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)

@start_page.route("/terminate_download_java/<hash>")
@only_on_startup
def terminate_downloading_java(hash):
    logger = logging.getLogger("ob_panel")
    rtn = returnModel("string")
    dp = DownloaderPool.getInstance()

    try:
        dp.terminate(hash)
        return rtn.success(True)
    except:
        return rtn.error(500)

#  download progress socket
@socketio.on("ask_download_progress")
@only_on_startup
def get_java_download_progress(msg):
    logger = logging.getLogger("ob_panel")
    _model = {
        "current": None,
        "total": None,
        "hash": msg,
        "finished": False
    }
    dp = DownloaderPool.getInstance()
    inst = dp.get(msg)
    if inst == None:
        _model["finished"] = True
    else:
        prog = inst.dl.getProgress()
        _model["current"] = prog[0]
        _model["total"] = prog[1]

        logger.debug(_model)

    emit("download_progress",_model)

# in step=3 (test MySQL connection)
@start_page.route("/test_mysql_connection", methods=["POST"])
@only_on_startup
def test_mysql_connection():
    rtn = returnModel(type="string")
    try:
        db_env = DatabaseEnv()
        F = request.form

        mysql_username = F.get("mysql_username")
        mysql_password = F.get("mysql_password")

        return rtn.success(db_env.testMySQLdb(mysql_username, mysql_password))
    except:
        return rtn.error(500)

# make sure use circusd!
def _restart_process():
    client = SystemProcessClient()
    client.send_restart_cmd("process_watcher")
    client.send_restart_cmd("websocket_server")
    client.send_restart_cmd("ftp_manager")
    client.send_restart_cmd("app")