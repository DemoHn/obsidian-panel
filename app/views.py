from app import app
from app.controller.global_config import GlobalConfig
from flask import render_template, redirect, send_file

def get_version():
    f = open("VERSION", "r")
    version = f.read()
    return version.strip()

version = get_version()
@app.route("/")
def index():
    gc = GlobalConfig.getInstance()
    _is_startup = gc.get("init_super_admin")

    if _is_startup == None or _is_startup == False:
        return redirect("/startup")
    else:
        return redirect("/server_inst/dashboard", version = version)

@app.route("/login")
def login():
    gc = GlobalConfig()

    if gc.get("init_super_admin") == True:
        login_flag = 1
    else:
        login_flag = 0
    return render_template("/startup/index.html", login_flag = login_flag, version = version)
# proxies
@app.route("/vendors-%s.js" % version)
def proxy_vendors_js():
    return send_file("static/js/vendors.build.js")
    pass

@app.route("/super_admin.app-%s.js" % version)
def proxy_sa():
    return send_file("static/js/super_admin.app.build.js")
    pass

@app.route("/server_inst.app-%s.js" % version)
def proxy_inst():
    return send_file("static/js/server_inst.app.build.js")
    pass

@app.route("/startup.app-%s.js" % version)
def proxy_startup():
    return send_file("static/js/startup.app.build.js")
    pass
