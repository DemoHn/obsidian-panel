__author__ = "Nigshoxiz"

# import models
from flask import Blueprint, render_template, abort, request, make_response
from jinja2 import TemplateNotFound
from app.utils import returnModel, salt

import hashlib
import traceback
from app import logger
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
def render_startup_page():
    return render_template("startup/index.html")

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
                java_env_index = F.get("java_env_index")
                gc.set("default_java_binary_id", java_env_index)
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
        F = request.form
        gc = GlobalConfig.getInstance()
        db = DatabaseEnv()

        db_env = F.get("db_env")

        if gc.get("temp_superadmin_username") == "" or \
            gc.get("temp_superadmin_hash") == "":
            return render_template("startup/startup_super_admin.html")

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
