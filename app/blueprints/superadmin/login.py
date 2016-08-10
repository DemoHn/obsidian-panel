__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound
from . import super_admin_page
from .check_login import check_login

from app import db
from app.model.ob_user import Users
from app.model.ob_token import UserToken

#import libs
import string, random
import logging

logger = logging.getLogger("ob_panel")

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
        if not Users.search_username(username):
            return render_template("superadmin/login.html",login_error="username_not_found")

        result = Users.compare_password(username, password)

        if result:
            _token_str = make_token(32)
            tk = UserToken(token=_token_str)
            tk.insert(username)

            # make response with cookie
            resp = make_response(redirect("/super_admin/main"))
            if remember_me == "on":
                resp.set_cookie('session_token',_token_str,max_age=24*10*3600)
            else:
                session['session_token'] = _token_str
            return resp
            #return render_template("superadmin/index.html")
        else:
            return render_template("superadmin/login.html", login_error="login_error")
    except TemplateNotFound:
        abort(404)

@super_admin_page.route("/logout", methods=["GET"])
def logout():
    resp = make_response(redirect("/super_admin/login"))
    # just set an empty cookie string
    resp.set_cookie("session_token","",max_age=0)
    return resp

@super_admin_page.route("/main")
@check_login
def main_page(uid):
    try:
        return render_template("superadmin/index.html")
    except TemplateNotFound:
        abort(404)