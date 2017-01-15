__author__ = "Nigshoxiz"

# import models
from flask import Blueprint, render_template, abort, request, make_response
from jinja2 import TemplateNotFound
from app.utils import returnModel, salt

import hashlib, os
import traceback
from app import logger
from functools import wraps
# import controllers
from app.controller.config_env import DatabaseEnv, JavaEnv
from app.controller.init_main_db import init_database, init_db_data
from app.controller.global_config import GlobalConfig
from app.controller.sys_process import SystemProcessClient
from app.tools.mc_downloader import  DownloaderPool

start_page = Blueprint("start_page", __name__,
                       template_folder='templates',
                       url_prefix="/startup")

rtn = returnModel("string")
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
def render_startup_page():
    return render_template("startup/index.html", login_flag = 0)

@start_page.route("/api/submit", methods=["POST"])
@only_on_startup
def starter_finish():
    try:
        F = request.json
        gc = GlobalConfig.getInstance()
        db = DatabaseEnv()

        db_env = F.get("db_env")

        usr_data = {
            "username" : F.get("username"),
            "email" : F.get("email"),
            "password" : F.get("password")
        }

        if db_env == "sqlite":
            db.setDatabaseType("sqlite")
            # set init flag = True
            gc.set("init_super_admin", "True")
            # then init database
            init_database()
            if init_db_data(usr_data):
                return rtn.success(True)
            else:
                return rtn.error(409)

        elif db_env == "mysql":
            db.setDatabaseType("mysql")

            _u = F.get("mysql_username")
            _p = F.get("mysql_password")

            if db.testMySQLdb(_u,_p) == True:
                gc.set("init_super_admin","True")

                db.setMySQLinfo(_u, _p)
                init_database()
                if init_db_data(usr_data):
                    return rtn.success(True)
                else:
                    return rtn.error(409)
            else:
                return rtn.error(409)
        else:
            return rtn.error(402)
    except:
        traceback.print_exc()
        return rtn.error(500)

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
        java_envs = {
            "system": [],
            "user" : []
        }
        __dir, __ver = env.findSystemJavaInfo()
        if __dir != None:
            _model = {
                "name" : "java",
                "dir" : "(%s)" % __dir
            }
            java_envs.get("system").append(_model)

        _arr = env.findUserJavaInfo()
        for java_ver in _arr:
            _model = {
                "name" : "JDK %s" % java_ver['version'],
                "dir" : "(%s)" % java_ver["dir"]
            }

            java_envs.get("user").append(_model)
        return rtn.success(java_envs)
    except:
        return rtn.error(500)
    pass

# in step=2 (test MySQL connection)
@start_page.route("/test_mysql_connection", methods=["POST"])
@only_on_startup
def test_mysql_connection():
    rtn = returnModel(type="string")
    try:
        db_env = DatabaseEnv()
        F = request.json

        mysql_username = F.get("mysql_username")
        mysql_password = F.get("mysql_password")

        return rtn.success(db_env.testMySQLdb(mysql_username, mysql_password))
    except:
        return rtn.error(500)

# make sure use circusd!
def _restart_process():
    os.system("ob-panel restart")
    #client = SystemProcessClient()
    #client.send_restart_cmd("task_scheduler")
    #client.send_restart_cmd("zeromq_broker")
    #client.send_restart_cmd("process_watcher")
    #client.send_restart_cmd("websocket_server")
    #client.send_restart_cmd("ftp_manager")
    #client.send_restart_cmd("app")
