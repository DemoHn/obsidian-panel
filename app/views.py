from app import app
from app.controller.global_config import GlobalConfig
from flask import render_template, redirect

import threading
@app.route("/")
def index():
    gc = GlobalConfig.getInstance()
    _is_startup = gc.get("init_super_admin")

    if _is_startup == None or _is_startup == False:
        return redirect("/startup")
    else:
        return redirect("/super_admin/login")

@app.route("/draft")
def __draft():
    return render_template("_draft.html")