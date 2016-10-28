__author__ = "Nigshoxiz"

from flask import render_template, abort, request, make_response, redirect, session
from jinja2 import TemplateNotFound
from . import server_inst_page
from app.blueprints.superadmin.check_login import check_login

from app.utils import PRIVILEGES
#import libs
import string, random
import logging


@server_inst_page.route("/logout", methods=["GET"])
def logout():
    resp = make_response(redirect("/super_admin/login"))
    # just set an empty cookie string
    resp.set_cookie("session_token","",max_age=0)
    # clear session
    session["session_token"] = ''
    return resp

@server_inst_page.route("/")
@check_login
def view(uid, priv):
    try:
        if priv <= PRIVILEGES.INST_OWNER:
            return render_template("server_inst/index.html")
        else:
            abort(403)
    except TemplateNotFound:
        abort(404)

