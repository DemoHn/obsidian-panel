import redis
import json
import pickle
import inspect

WS_TAG = "CLIENT"
class MessageQueueProxy(object):
    instance = None
    '''
    What is a .. Message Queue Proxy?
    A message queue proxy is responsible for receiving message from message queue
    and send message to it.
    Because we use a standalone websocket server, we use message queue to delegate
    websocket server to send websocket message, instead of sending message directly.
    '''
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

    def listen(self):
        from websocket_server.server import WSConnections,mgr
        for msg in self.pubsub.listen():
            channel = self.channel.encode()

            if msg["type"] == "message" and msg['channel'] == channel:
                msg_json = pickle.loads(msg["data"])

                dest = msg_json.get("to")
                event_name = msg_json.get("event")
                values = msg_json.get("props")
                if dest == WS_TAG and event_name != None and values != None:
                    ws = WSConnections.getInstance()
                    _uid = msg_json.get("_uid")

                    if _uid != None:
                        _s = {
                            # prevent infinite handling
                            "to" : "CLIENT_BYE",
                            "event": event_name,
                            "props": values
                        }
                        ws.send_data("message", _s, _uid)
                    else:
                        send_msg = {
                            "method": "emit",
                            "event": "message",
                            "data": {
                                "event": event_name,
                                "to": "CLIENT_BYE",
                                "props": values
                            },
                            "namespace": "/",
                            "room": None,
                            "skip_sid": None,
                            "callback": None
                        }

                        mgr.redis.publish(self.channel, pickle.dumps(send_msg))


