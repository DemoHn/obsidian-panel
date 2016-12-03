from app import db
from app.model import Users, UserToken
from app.controller.global_config import GlobalConfig
from app.utils import PRIVILEGES
from app.tools.mq_proxy import WS_TAG, MessageQueueProxy
import socketio
import eventlet
import json
import re
import threading
import pickle

eventlet.monkey_patch()

mgr = socketio.RedisManager("redis://")
sio = socketio.Server(client_manager=mgr)

class WSConnections(object):
    instance = None

    @staticmethod
    def getInstance():
        if WSConnections.instance == None:
            WSConnections.instance = WSConnections()
        return WSConnections.instance

    def __init__(self):
        # KEY :  <user_key> = user_{%uid}
        # VALUE : [<sid1>, <sid2>, ...]
        self.connections = {}
        self._init_connect_event()
        self._init_disconnect_event()

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
        @sio.on("connect")
        def on_connect(sid, environment):
            priv, uid = self._check_user(environment)
            # socket is invalid
            if priv == None:
                sio.disconnect(sid, namespace="/")
            else:
                user_key = "user_%s" % uid
                if self.connections.get(user_key) == None:
                    self.connections[user_key] = []

                if sid not in self.connections.get(user_key):
                    self.connections[user_key].append(sid)

    def _init_disconnect_event(self):
        @sio.on("disconnect", namespace="/")
        def on_disconnect(sid):
            for user_key in self.connections:
                if sid in self.connections.get(user_key):
                    self.connections.get(user_key).remove(sid)

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
            sio.emit(event, data, room=sid, namespace="/")
        elif uid == None:
            return None
        else:
            user_key = "user_%s" % uid
            sessions = self.connections.get(user_key)
            if sessions != None:
                for sid in sessions:
                    sio.emit(event, data, room=sid, namespace="/")

@sio.on('message', namespace="/")
def emit_message(sid, data):
    proxy = MessageQueueProxy(WS_TAG.CONTROL)

    ws = WSConnections.getInstance()

    _flag  = data.get("flag")
    _event = data.get("event")
    _props = data.get("props")

    # only root user could operate it
    avail = ws.sid_available(sid, permission=PRIVILEGES.ROOT_USER)

    if avail == True:
        # from CLIENT -> CONTROL
        #
        proxy.send(_flag, _event, _props, WS_TAG.CONTROL,
                   uid = ws.find_uid(sid),
                   sid = sid,
                   _src= WS_TAG.CLIENT)

@sio.on('message_startup', namespace="/")
def emit_message_startup(sid, data):
    proxy = MessageQueueProxy(WS_TAG.CONTROL)
    _flag  = data.get("flag")
    _event = data.get("event")
    _props = data.get("props")
    proxy.send(_flag, _event, _props, WS_TAG.CONTROL,
               uid = 0,
               sid = sid,
               _src= WS_TAG.CLIENT)


def start_websocket_server():
    from .controller import ProcessEventHandler, DownloaderEventHandler
    # register listeners
    #ControllerOfInstance()
    #init
    WSConnections.getInstance()
    # add listen thread
    #proxy = MessageQueueProxy.getInstance()
    #t = threading.Thread(target=proxy.listen)
    #t.start()

    proxy = MessageQueueProxy(WS_TAG.CONTROL)
    proxy.register(ProcessEventHandler)
    proxy.register(DownloaderEventHandler)

    proxy.listen(background=True)

    app = socketio.Middleware(sio)
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)
