from app import db
from app.model import Users, UserToken

import socketio
import eventlet
import pickle
from flask import session, request
from functools import wraps

eventlet.monkey_patch()

mgr = socketio.RedisManager("redis://")
sio = socketio.Server(client_manager=mgr)

class WSConnections(object):
    def __init__(self):
        # KEY :  <user_key> = user_{%uid}
        # VALUE : [<sid1>, <sid2>, ...]
        self.connections = {}
        self._init_connect_event()
        self._init_disconnect_event()

    def _check_user(self, request):
        _token = session.get("session_token")

        if _token == None or _token == '':
            # read token
            _token = request.cookies.get("session_token")

        if _token == None:
            return (None, None)

        user = db.session.query(UserToken).join(Users).filter(UserToken.token == _token).first()
        if user is None:
            return (None, None)
        else:
            priv = user.ob_user.privilege
            uid = user.uid

            return (priv, uid)

    def _init_connect_event(self):
        @sio.on("connect", namespace="/")
        def on_connect():
            sid = request.sid

            priv, uid = self._check_user(request)
            # socket is invalid
            if priv == None:
                sio.disconnect(sid,namespace="/")
            else:
                user_key = "user_%s" % uid
                if self.connections.get(user_key) == None:
                    _conns = self.connections
                    _conns[user_key] = []

                if sid not in self.connections.get(user_key):
                    self.connections.get(user_key).append(sid)
                    #emit("ack",{"sid":sid})

    def _init_disconnect_event(self):
        @sio.on("disconnect", namespace="/")
        def on_disconnect():
            sid = request.sid

            priv, uid = self._check_user(request)
            # socket invalid, if invalid, let it go
            if priv != None:
                user_key = "user_%s" % uid
                if self.connections.get(user_key) != None:
                    sids = self.connections.get(user_key)
                    try:
                        # delete sid from sid list
                        sids.remove(sid)
                    finally:
                        return None

    def send_data(self, event, data, uid):
        '''
        send websocket data to all session that belongs to the user
        '''
        user_key = "user_%s" % uid
        sessions = self.connections.get(user_key)
        if sessions != None:
            for sid in sessions:
                sio.emit(event, data, room=sid, namespace="/channel_inst")

@sio.on('message', namespace="/")
def emit_message(sid, data):
    mgr.redis.publish("socketio",pickle.dumps(data))

def start_websocket_server():
    #init
    WSConnections()
    app = socketio.Middleware(sio)
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)