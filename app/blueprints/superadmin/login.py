__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from flask_socketio import emit, send
from jinja2 import TemplateNotFound
from . import super_admin_page, logger
from .check_login import super_admin_only

from app.model import Users, UserToken
from app import db
import traceback
#import libs
import string, random

from app.utils import PRIVILEGES
@super_admin_page.route("/login", methods=["GET"])
def get_login_page():
    try:
        return render_template("superadmin/login.html", login_error = None)
    except TemplateNotFound:
        abort(404)

@super_admin_page.route("/login", methods=["POST"])
def login():

    def make_token(digits):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(digits))

    try:
        F = request.form
        username = F.get("username")
        password = F.get("password")

        remember_me = F.get("remember_me")
        #if not Users.search_username(username):
        if db.session.query(Users).filter(Users.username == username).first() == None:
            return render_template("superadmin/login.html",login_error="username_not_found")

        result, _user = Users.compare_password(username, password)

        if result:
            _token_str = make_token(32)
            tk = UserToken(token=_token_str)
            tk.insert(username)

            # redirect different page as account types differ
            if _user.privilege == PRIVILEGES.ROOT_USER:
                # make response with cookie
                resp = make_response(redirect("/super_admin/"))
            elif _user.privilege == PRIVILEGES.INST_OWNER:
                resp = make_response(redirect("/server_inst/"))
            else:
                resp = make_response()
            # `remember me` checkbox ticked
            if remember_me == "on":
                resp.set_cookie('session_token',_token_str,max_age=24*10*3600)
            else:
                # session
                resp.set_cookie("session_token", _token_str, expires=None)
                #session['session_token'] = _token_str

            return resp
            #return render_template("superadmin/index.html")
        else:
            return render_template("superadmin/login.html", login_error="login_error")
    except TemplateNotFound:
        abort(404)
    except:
        traceback.print_exc()
        abort(500)


@super_admin_page.route("/logout", methods=["GET"])
def logout():
    resp = make_response(redirect("/super_admin/login"))
    # just set an empty cookie string
    resp.set_cookie("session_token", "", max_age=0)
    # clear session
    session["session_token"] = ''
    return resp

# main page
@super_admin_page.route("/")
@super_admin_only
def main_page(uid, priv):
    try:
        if priv == PRIVILEGES.ROOT_USER:
            #return render_template("superadmin/index.html")
            # TEST
            return render_template("server_inst/new_inst.html")
        else:
            abort(403)
    except TemplateNotFound:
        abort(404)