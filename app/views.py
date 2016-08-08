from app import app
from app.controller.global_config import GlobalConfig
from flask import render_template, redirect

import threading
@app.route("/")
def index():
    gc = GlobalConfig.getInstance()
    if gc.get("init_super_admin") == False:
        return redirect("/startup")
    else:
        return render_template("superadmin/index.html")

@app.route("/draft")
def __draft():
    return render_template("_draft.html")