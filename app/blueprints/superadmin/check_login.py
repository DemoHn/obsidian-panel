__author__ = "Nigshoxiz"

from flask import Blueprint, render_template, abort, request, redirect, session
from app.model import UserToken, Users
from app import db
from functools import wraps
from app.utils import returnModel
from app.controller.global_config import GlobalConfig
from app.utils import PRIVILEGES
# check if user is login

###########################################
#         check login decorator           #
###########################################

# write database uri
gc = GlobalConfig.getInstance()
if gc.get("database_uri") != None:
    db.app.config["SQLALCHEMY_DATABASE_URI"] = gc.get("database_uri")

def check_login(fn):
    @wraps(fn)
    def dec_function(*args, **kwargs):
        # read session (remember me == false)
        session_token = session.get("session_token")

        if session_token == None or session_token == '':
            # read token
            session_token = request.cookies.get("session_token")

        if session_token == None:
            return redirect("/super_admin/login")
        else:
            # query login user via token
            user = db.session.query(UserToken).join(Users).filter(UserToken.token == session_token).first()
            if user is None:
                return redirect("/super_admin/login")
            else:
                priv = user.ob_user.privilege
                uid = user.uid

                return fn(uid, priv, *args, **kwargs)
    return dec_function

def ws_check_token(fn):
    @wraps(fn)
    def decorated_function(msg, *args, **kwargs):
        _token = session.get("session_token")

        if _token == None or _token == '':
            # read token
            _token = request.cookies.get("session_token")

        if _token == None:
            return None

        user = db.session.query(UserToken).join(Users).filter(UserToken.token == _token).first()
        #
        if user is None:
            return None
        else:
            priv = user.ob_user.privilege
            uid = user.uid

            return fn(msg, uid, priv, *args, **kwargs)
    return decorated_function

def ajax_check_login(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        rtn = returnModel("string")
        # read session (remember me == false)
        session_token = session.get("session_token")

        if session_token == None or session_token == '':
            # read token
            session_token = request.cookies.get("session_token")

        if session_token == None:
            return rtn.error(403)
        else:
            # query login user via token
            user = db.session.query(UserToken).join(Users).filter(UserToken.token == session_token).first()
            if user is None:
                return rtn.error(403)
            else:
                priv = user.ob_user.privilege
                uid = user.uid

                return fn(uid, priv, *args, **kwargs)

    return decorated_function
###############################################
# super_admin_only
###############################################

def super_admin_only(fn):
    @wraps(fn)
    def dec_function(*args, **kwargs):
        # read session (remember me == false)
        session_token = session.get("session_token")

        if session_token == None or session_token == '':
            # read token
            session_token = request.cookies.get("session_token")

        if session_token == None:
            return redirect("/super_admin/login")
        else:
            # query login user via token
            user = db.session.query(UserToken).join(Users).filter(UserToken.token == session_token).first()
            if user is None:
                return redirect("/super_admin/login")
            else:
                priv = user.ob_user.privilege
                uid = user.uid

                if priv == PRIVILEGES.ROOT_USER:
                    return fn(uid, priv, *args, **kwargs)
                else:
                    return redirect('/super_admin/login')

    return dec_function

def ws_super_admin_only(fn):
    @wraps(fn)
    def decorated_function(msg, *args, **kwargs):
        _token = session.get("session_token")

        if _token == None or _token == '':
            # read token
            _token = request.cookies.get("session_token")

        if _token == None:
            return None

        user = db.session.query(UserToken).join(Users).filter(UserToken.token == _token).first()
        #
        if user is None:
            return None
        else:
            priv = user.ob_user.privilege
            uid = user.uid

            if priv == PRIVILEGES.ROOT_USER:
                return fn(msg, uid, priv, *args, **kwargs)
            else:
                return None

    return decorated_function

def ajax_super_admin_only(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        rtn = returnModel("string")
        # read session (remember me == false)
        session_token = session.get("session_token")

        if session_token == None or session_token == '':
            # read token
            session_token = request.cookies.get("session_token")

        if session_token == None:
            return rtn.error(403)
        else:
            # query login user via token
            user = db.session.query(UserToken).join(Users).filter(UserToken.token == session_token).first()
            if user is None:
                return rtn.error(403)
            else:
                priv = user.ob_user.privilege
                uid = user.uid

                if priv == PRIVILEGES.ROOT_USER:
                    return fn(uid, priv, *args, **kwargs)
                else:
                    return rtn.error(403)

    return decorated_function