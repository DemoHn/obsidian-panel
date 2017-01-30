from app import db
from app.model import Users, UserToken
from app.controller.global_config import GlobalConfig
from app.utils import PRIVILEGES
from app.tools.mq_proxy import WS_TAG, MessageQueueProxy

from . import logger
import socketio, eventlet, json, re, threading, traceback

class WSConnections(object):

    instance = None
    @staticmethod
    def getInstance(sio=None):
        if WSConnections.instance == None:
            WSConnections.instance = WSConnections(sio)
        _i = WSConnections.instance
        if sio != None:
            _i.sio = sio
        return _i

    def __init__(self, sio):
        # KEY :  <user_key> = user_{%uid}
        # VALUE : [<sid1>, <sid2>, ...]
        self.sio = sio
        self.connections = {}

    def init_events(self):
        self._init_connect_event()
        self._init_disconnect_event()
        self._init_message_event()

    def _check_user(self, environment):

        def _construct_cookie(headers_raw):
            '''
            format: ((<key>,<value>), .. )
            For cookies:
            ('Cookie', 'A=B; C=D')
            :param headers_raw:
            :return:
            '''
            cookies = {}
            _re = "^(.+)=(.+)"
            for x in range(0, len(headers_raw)):
                _key , _val = headers_raw[x]

                if _key.lower() == "cookie":
                    _cookie_str = _val
                    _cookie_str_arr = _cookie_str.split(" ")
                    for _cookie_item in _cookie_str_arr:
                        r = re.search(_re, _cookie_item)
                        if r != None:
                            cookies[r.group(1)] = r.group(2)
                    break
            return cookies

        gc = GlobalConfig.getInstance()
        if gc.get("init_super_admin") == False:
            return (1, 0)

        # after  initialization
        cookies = _construct_cookie(environment["headers_raw"])
        _token = cookies.get("session_token")

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
        @self.sio.on("connect")
        def on_connect(sid, environment):
            priv, uid = self._check_user(environment)
            # socket is invalid
            if priv == None:
                self.sio.disconnect(sid, namespace="/")
            else:
                user_key = "user_%s" % uid
                if self.connections.get(user_key) == None:
                    self.connections[user_key] = []

                if sid not in self.connections.get(user_key):
                    self.connections[user_key].append(sid)

    def _init_disconnect_event(self):
        @self.sio.on("disconnect", namespace="/")
        def on_disconnect(sid):
            for user_key in self.connections:
                if sid in self.connections.get(user_key):
                    self.connections.get(user_key).remove(sid)

    def _init_message_event(self):
        @self.sio.on('message', namespace="/")
        def emit_message(sid, data):
            _event = data.get("event")
            _props = data.get("props")

            # only root user could operate it
            # TODO extend priv range
            avail = self.sid_available(sid, permission=PRIVILEGES.ROOT_USER)

            if avail == True:
                logger.debug("send <-- event = %s, props = %s" % (_event, _props))
            else:
                logger.debug("reject <-- event = %s, props = %s" % (_event, _props))

    def sid_available(self, sid, permission = None):
        if permission == None:
            return True
        else:
            _uid = None
            _priv = None
            for user_key in self.connections:
                if sid in self.connections.get(user_key):
                    _uid = user_key[5:]
                    break
            if _uid == None:
                return False
            else:
                user_obj = db.session.query(Users).filter(Users.id == int(_uid)).first()
                if user_obj == None:
                    return False
                else:
                    _priv = user_obj.privilege

            if _priv > permission:
                return False
            else:
                return True

    def find_uid(self, sid):
        _uid = None
        for user_key in self.connections:
            if sid in self.connections.get(user_key):
                _uid = user_key[5:]
                break
        return _uid

    def send_data(self, event, data, uid = None, sid = None):
        '''
        send websocket data to all session that belongs to the user
        '''
        if sid != None:
            logger.debug("send <-- sid = %s, content = %s" % (sid[0:6], data))
            self.sio.emit(event, data, room=sid, namespace="/")
        elif uid == None:
            return None
        else:
            user_key = "user_%s" % uid
            sessions = self.connections.get(user_key)
            if sessions != None:
                logger.debug("send[B] <-- uid = %s, content = %s" % (uid, data))
                for sid in sessions:
                    self.sio.emit(event, data, room=sid, namespace="/")
