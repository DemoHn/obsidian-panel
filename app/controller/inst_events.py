from app import socketio, db
from app.model import Users, UserToken

from flask_socketio import emit, send, disconnect
from flask import request, session

import logging

logger = logging.getLogger("ob_panel")

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
        @socketio.on("connect")
        def on_connect():
            sid = request.sid
            priv, uid = self._check_user(request)
            # socket is invalid
            if priv == None:
                disconnect()
            else:
                user_key = "user_%s" % uid
                if self.connections.get(user_key) == None:
                    _conns = self.connections
                    _conns[user_key] = []

                self.connections.get(user_key).append(sid)
                emit("ack",{"sid":sid})

    def _init_disconnect_event(self):
        @socketio.on("disconnect")
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
                emit(event, data, room=sid)

class InstanceEventEmitter(object):
    '''
    emit websocket on some events
    '''
    def __init__(self, add_hook_func):
        self.add_hook_func = add_hook_func

        _names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout",
                  "inst_player_change","inst_memory_change")
        # add hook function
        for item in _names:
            _method = getattr(self, "on_%s" % item)
            self.add_hook_func(item, _method)

        self.ws = WSConnections()

    def _send_web_socket(self, event_name, data):
        pass

    def on_inst_starting(self, inst_id, p):
        print("<inst %s> start initialize" % inst_id)
        pass

    def on_inst_running(self, inst_id, p):
        print("<inst %s> start running. Time %s" % (inst_id, p))
        pass

    def on_log_update(self, inst_id, p):
        print(p)
        pass

    def on_connection_lost(self, inst_id, p):
        pass

    def on_inst_terminate(self, inst_id, p):
        print("<inst %s> stopped!" % inst_id)
        pass

    def on_inst_player_login(self, inst_id ,p):
        print("<inst %s> login" % inst_id)
        print(p)
        pass

    def on_inst_player_logout(self, inst_id, p):
        print("<inst %s> logout" % inst_id)
        print(p)
        pass

    def on_inst_player_change(self, inst_id, p):
        online, total = p
        print("<inst %s> online player: %s" % (inst_id, online))
        pass

    def on_inst_memory_change(self, inst_id, p):
        mem = p
        print("<inst %s> memory : %s" % (inst_id, mem))
        pass