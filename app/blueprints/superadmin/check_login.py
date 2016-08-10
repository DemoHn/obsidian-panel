__author__ = "Nigshoxiz"

from flask import Blueprint, render_template, abort, request, redirect, session
from app.model.ob_token import UserToken
from app.model.ob_user import Users
from app import db
from functools import wraps

# check if user is login
def check_login(fn):
    def decorated_function(*args, **kwargs):
        # read session (remember me == false)
        session_token = session.get("session_token")

        if session_token == None or session_token == '':
            # read token
            session_token = request.cookies.get("session_token")

        if session_token == None:
            return redirect("/super_admin/login")
        else:
            user = db.session.query(UserToken).join(Users).filter(UserToken.token==session_token).first()
            if user is None:
                return redirect("/super_admin/login")
            else:
                priv = user.ob_user.privilege
                uid = user.uid
                return fn(uid, priv, *args, **kwargs)

    return decorated_function
