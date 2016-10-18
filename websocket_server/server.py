from app import db
from app.model import Users, UserToken

from app.utils import PRIVILEGES
import socketio
import eventlet
import pickle
import re


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
                    _conns = self.connections
                    _conns[user_key] = []

                if sid not in self.connections.get(user_key):
                    self.connections.get(user_key).append(sid)
                    #emit("ack",{"sid":sid})

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

    def send_data(self, event, data, uid):
        '''
        send websocket data to all session that belongs to the user
        '''
        user_key = "user_%s" % uid
        sessions = self.connections.get(user_key)
        if sessions != None:
            for sid in sessions:
                sio.emit(event, data, room=sid, namespace="/")

@sio.on('message', namespace="/")
def emit_message(sid, data):
    _send_data_model = {
        "to" : data.get("to"),
        "props": data.get("props"),
        "event": data.get("event")
    }

    ws = WSConnections.getInstance()
    # only root user could operate it
    avail = ws.sid_available(sid, permission=PRIVILEGES.ROOT_USER)

    if avail == True:
        mgr.redis.publish("socketio",pickle.dumps(_send_data_model))

def start_websocket_server():
    #init
    w = WSConnections.getInstance()
    app = socketio.Middleware(sio)
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)

'''

protocol :
[PUB]
{
   "event" : "<namespace>"."<event name>",
   "to": "MPW",
   "props": {}
}

'''