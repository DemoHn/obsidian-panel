from app import app, socketio
from app.controller.global_config import GlobalConfig
from flask import render_template, redirect
from flask_socketio import send, emit

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

@socketio.on('test_ws')
def test_ws(msg):
    print(msg)
    send(msg)