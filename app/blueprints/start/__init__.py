__author__ = "Nigshoxiz"

# import models
from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from app import socketio
from app.utils import returnModel, salt
import hashlib
# import controllers
from app.controller.config_env import DatabaseEnv
from app.controller.global_config import GlobalConfig

start_page = Blueprint("start_page", __name__,
                       template_folder='templates',
                       url_prefix="/start")

@start_page.route("/", methods=["GET"])
def show_starter_page():
    try:
        _step = request.args.get("step")

        if _step == None:
            _step = 1
        _step = int(_step)

        if _step == 1:
            return render_template("start/step_1.html")
        elif _step == 2:
            return render_template("start/step_2.html")
        elif _step == 3:
            return render_template("start/step_3.html")
        else:
            abort(404)
    except TemplateNotFound:
        abort(404)

@start_page.route("/", methods=["POST"])
def handle_init_config():
    try:
        F = request.form
        _step = request.args.get('step')
        _step = int(_step)
        if _step == 2:
            email = F.get("email")
            username = F.get("username")
            password = F.get("password")
            privilege = 1

            try:
                # NOTICE: At the beginning, we use temperate sqlite database to store superadmin's
                # username and password. Then after initialization, just migrate them to the formal
                # database.
                gc = GlobalConfig.getInstance()
                gc.set("temp_superadmin_username", username)
                gc.set("temp_superadmin_email", email)
                gc.set("temp_superadmin_hash", hashlib.md5(password.encode('utf-8')+salt).hexdigest())

            except:
                return abort(500)
            return render_template("start/step_2.html")
        elif _step == 3:
            return render_template("start/step_3.html")
        else:
            abort(404)
    except TemplateNotFound:
        abort(404)

@start_page.route("/finish", methods=["POST"])
def init_finish():
    try:
        F = request.form
        return render_template("start/finish.html")
    except TemplateNotFound:
        abort(404)

# ajax data
#
# in step=2 (detect Java Environment)
#
# NOTE : this route (and the following 'download java' route) is somehow dangerous since anyone has privilege
# to operate. Thus, it's better to warn users to finish the starter steps as soon as possible.
@start_page.route("/detect_java_environment")
def detect_java_environment():
    pass

@start_page.route("/download_java")
def download_java():
    pass

# in step=3 (test MySQL connection)
@start_page.route("/test_mysql_connection", methods=["POST"])
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

'''
@socketio.on('my event')
def handle_my_custom_event(wtf):
    print(wtf)
'''