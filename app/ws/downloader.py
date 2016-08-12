__author__ = "Nigshoxiz"

from functools import wraps
from flask_socketio import disconnect
from flask import session, request

from app.utils import returnModel
from app import socketio, app, db
from app.tools.mc_downloader import DownloaderPool

from app.model.ob_token import UserToken
from app.model.ob_user import Users

###########################################
#         check login decorator           #
###########################################
def ws_check_token(msg, fn):
    @wraps(fn)
    def decorated_function(msg, *args, **kwargs):
        _token = msg.get("token")

        if _token == None:
            disconnect()

        user = db.session.query(UserToken).join(Users).filter(UserToken.token == _token).first()
        #
        if user is None:
            disconnect()
        else:
            priv = user.ob_user.privilege
            uid = user.uid
            return fn(msg, uid, priv, *args, **kwargs)
    return decorated_function

def ajax_check_login(fn):
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

