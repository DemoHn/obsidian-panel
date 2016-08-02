from flask import render_template,request, redirect
from app.controller.start.global_config import GlobalConfig

from app import db, app
from app.model.ob_user import AdminUsers
from datetime import datetime

@app.route("/")
def index():
    gc = GlobalConfig.getInstance()
    if gc.get("init_super_admin") == False:
        return redirect("/start")
    else:
        return render_template("superadmin/index.html")

@app.route("/draft")
def __draft():
    return render_template("_draft.html")