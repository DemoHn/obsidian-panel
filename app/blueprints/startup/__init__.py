__author__ = "Nigshoxiz"

# import models
from flask import Blueprint, render_template, abort, request, make_response
from jinja2 import TemplateNotFound
from app.utils import returnModel, salt

import hashlib, os, yaml
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

def get_version():
    f = open("VERSION", "r")
    version = f.read()
    return version.strip()

@start_page.route("/", methods=["GET"])
@only_on_startup
def render_startup_page():
    version = get_version()
    return render_template("startup/index.html", login_flag = 0, version = version)

# dump yaml data
def dump_yaml_config(new_config):
    docs = None
    text = ""
    try:
        config_file = "config.yaml"
        fr = open(os.path.join(os.getcwd(), config_file), "r")
        docs = yaml.load(fr)
        text = fr.read()
        fr.close()
    except:
        fr.close()
        logger.error(traceback.format_exc())
        return False

    try:
        fw = open(os.path.join(os.getcwd(), config_file), "w")
        # change config
        docs["circus"]["end_port"] = int(new_config.get("pm_port"))
        docs["server"]["listen_port"] = int(new_config.get("app_port"))
        docs["redis"]["listen_port"] = int(new_config.get("redis_port"))
        docs["ftp"]["listen_port"] = int(new_config.get("ftp_port"))
        docs["broker"]["listen_port"] = int(new_config.get("msgQ_port"))

        dump_text = yaml.dump(docs, default_flow_style=False)
        if dump_text != "" and dump_text != None:
            fw.write(dump_text)
        fw.close()
        return True
    except:
        fw.close()
        logger.error(traceback.format_exc())
    return False

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

        port_config = {
            "app_port" : F.get("app_port"),
            "ftp_port" : F.get("ftp_port"),
            "msgQ_port" : F.get("msgQ_port"),
            "redis_port" : F.get("redis_port"),
            "pm_port" : F.get("pm_port")
        }

        if not dump_yaml_config(port_config):
            return rtn.error(500)

        if db_env == "sqlite":
            db.setDatabaseType("sqlite")
            # set init flag = True
            gc.set("init_super_admin", "True")
            gc.set("_RESTART_LOCK", "True")
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
                gc.set("_RESTART_LOCK", "True")
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
    return rtn.success(200)
#    return response

# DEPRECATED!!!!
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
