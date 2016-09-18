from app import socketio, db
from app.model import Users, UserToken, ServerInstance

from flask_socketio import emit, send, disconnect, join_room, leave_room, rooms
from flask import request, session

import logging

logger = logging.getLogger("ob_panel")

class WSConnections(object):
    def __init__(self, watcher_obj):
        # KEY :  <user_key> = user_{%uid}
        # VALUE : [<sid1>, <sid2>, ...]
        self.connections = {}
        self.watcher = watcher_obj

        self._init_connect_event()
        self._init_disconnect_event()
        self._init_command_input_event()

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
                join_room(user_key)
                print(rooms())
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
                        leave_room(user_key)
                    finally:
                        return None

    def _init_command_input_event(self):
        @socketio.on("command_input")
        def on_command_input(cmd):
            cmd_str = cmd["command"]
            priv, uid = self._check_user(request)
            # get inst id
            # TODO multi instances for one user support
            inst_obj = db.session.query(ServerInstance).filter(ServerInstance.owner_id == uid).first()

            if inst_obj != None:
                inst_id = inst_obj.inst_id
                self.watcher.send_command(inst_id, cmd_str)

    def send_data(self, event, data, uid):
        '''
        send websocket data to all session that belongs to the user
        '''
        user_key = "user_%s" % uid
        sessions = self.connections.get(user_key)
        if sessions != None:
            for sid in sessions:
                socketio.emit(event, data, room=user_key)

class InstanceEventEmitter(object):
    '''
    emit websocket on some events
    '''
    def __init__(self, watcher_obj):
        self.add_hook_func = watcher_obj.add_hook

        _names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout",
                  "inst_player_change","inst_memory_change")
        # add hook function
        for item in _names:
            _method = getattr(self, "on_%s" % item)
            self.add_hook_func(item, _method)

        self.conn = WSConnections(watcher_obj)

        # KEY : <inst_id>
        # VALUE : <uid>
        self._inst_uid_cache = {}
        # refresh cache the first time
        self._get_uid_from_inst_id(0)

    def _get_uid_from_inst_id(self, inst_id):
        inst_key = "inst_%s" % inst_id
        if self._inst_uid_cache.get(inst_key) != None:
            return self._inst_uid_cache.get(inst_key)
        else:
            # read from database
            owners = db.session.query(ServerInstance).all()
            for serv_inst in owners:
                inst_key = "inst_%s" % serv_inst.inst_id
                self._inst_uid_cache[inst_key] = serv_inst.owner_id

            return self._inst_uid_cache.get(inst_key)

    def on_inst_starting(self, inst_id, p):
        print("<inst %s> start initialize" % inst_id)
        pass

    def on_inst_running(self, inst_id, p):
        print("<inst %s> start running. Time %s" % (inst_id, p))
        pass

    def on_log_update(self, inst_id, p):
        log_str = p
        uid = self._get_uid_from_inst_id(inst_id)

        log_dict = {
            "log": log_str
        }
        self.conn.send_data("log_update", log_dict, uid)
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