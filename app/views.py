from app import app
from app.controller.global_config import GlobalConfig
from flask import render_template, redirect, send_file

@app.route("/")
def index():
    gc = GlobalConfig.getInstance()
    _is_startup = gc.get("init_super_admin")

    if _is_startup == None or _is_startup == False:
        return redirect("/startup")
    else:
        return redirect("/server_inst/dashboard")

@app.route("/login")
def login():
    return render_template("/startup/index.html", login_flag = 1)
# proxies
@app.route("/vendors.js")
def proxy_vendors_js():
    return send_file("static/js/vendors.build.js")
    pass

@app.route("/super_admin.app.js")
def proxy_sa():
    return send_file("static/js/super_admin.app.build.js")
    pass

@app.route("/server_inst.app.js")
def proxy_inst():
    return send_file("static/js/server_inst.app.build.js")
    pass

@app.route("/startup.app.js")
def proxy_startup():
    return send_file("static/js/startup.app.build.js")
    pass

@app.route("/__test")
def __draft():
    return render_template("__test.html")
