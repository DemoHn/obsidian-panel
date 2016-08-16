__author__ = "Nigshoxiz"

from flask import Blueprint, render_template, abort, request, redirect, session
from app.model.ob_token import UserToken
from app.model.ob_user import Users
from app import db
from functools import wraps

# check if user is login

###########################################
#         check login decorator           #
###########################################

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