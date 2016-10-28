from app import app, socketio
from app.controller.global_config import GlobalConfig
from flask import render_template, redirect
from flask_socketio import send, emit

@app.route("/")
def index():
    gc = GlobalConfig.getInstance()
    _is_startup = gc.get("init_super_admin")

    if _is_startup == None or _is_startup == False:
        return redirect("/startup")
    else:
        return redirect("/server_inst/dashboard")

@app.route("/__test")
def __draft():
    return render_template("__test.html")

# TODO socketio
@socketio.on('test_ws')
def test_ws(msg):
    print(msg)
    emit('hello',msg)