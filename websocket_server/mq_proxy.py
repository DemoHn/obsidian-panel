import redis
import json
import pickle
import inspect
import uuid
from app.utils import WS_TAG

class MessageQueueProxy(object):
    instance = None

    @staticmethod
    def getInstance():
        if MessageQueueProxy.instance == None:
            MessageQueueProxy.instance = MessageQueueProxy()
        return MessageQueueProxy.instance

    def __init__(self):
        self.redis = redis.Redis()
        self.pubsub = self.redis.pubsub()

        self.channel = "socketio"
        # subscribe socketio to recv data from websocket server
        self.pubsub.subscribe(self.channel)

        self.handlers = {}


    def get_flag(self, flag):
        if flag == None:
            return uuid.uuid4()
        else:
            return flag

    def listen(self):
        from websocket_server.server import WSConnections,mgr
        for msg in self.pubsub.listen():
            channel = self.channel.encode()

            if msg["type"] == "message" and msg['channel'] == channel:
                msg_json = pickle.loads(msg["data"])

                dest = msg_json.get("to")
                event_name = msg_json.get("event")
                values = msg_json.get("props")

                flag = self.get_flag(msg_json.get("flag"))
                if dest == WS_TAG.CLIENT and event_name != None and values != None:
                    ws = WSConnections.getInstance()
                    _uid = msg_json.get("_uid")

                    if _uid != None:
                        _s = {
                            # prevent infinite handling
                            "to" : WS_TAG.CLIENT_BYE,
                            "event": event_name,
                            "props": values,
                            "flag" : flag
                        }
                        ws.send_data("message", _s, _uid)
                    else:
                        sid = msg_json.get("_sid")
                        if sid == None:
                            # just drop the message
                            return None

                        send_msg = {
                            "method": "emit",
                            "event": "message",
                            "data": {
                                "event": event_name,
                                "to": WS_TAG.CLIENT_BYE,
                                "props": values,
                                "flag" : flag
                            },
                            "namespace": "/",
                            "room": sid,
                            "skip_sid": None,
                            "callback": None
                        }

                        mgr.redis.publish(self.channel, pickle.dumps(send_msg))

                elif dest == WS_TAG.CLIENT_CONTROL and event_name != None and values != None:
                    _uid = msg_json.get("_uid")
                    _sid = msg_json.get("_sid")
                    _from = msg_json.get("_from")
                    # add info about uid
                    values["_uid"] = _uid
                    values["_sid"] = _sid
                    values["_from"] = _from

                    if self.handlers.get(event_name) != None:
                        handler = self.handlers.get(event_name)
                        handler(flag, values)

    def send(self, event, dest, flag, values):
        send_msg = {
            "event": event,
            "to": dest,
            "flag": flag,
            "props": values,
            "_uid": values.get("_uid"),
            "_sid": values.get("_sid"),
            "_from": WS_TAG.CLIENT_CONTROL
        }
        self.redis.publish(self.channel, pickle.dumps(send_msg))


def register_handler(self, event_name, handler):
    if inspect.ismethod(handler) or inspect.isfunction(handler):
        self.handlers[event_name] = handler

