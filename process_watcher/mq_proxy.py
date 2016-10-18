import redis
import json
import pickle
import inspect
WS_TAG = "MPW"
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

        self.handlers = []

    def listen(self):
        for msg in self.pubsub.listen():
            channel = self.channel.encode()
            if msg["type"] == "message" and msg['channel'] == channel:
                msg_json = pickle.loads(msg["data"])

                dest = msg_json.get("to")
                event_name = msg_json.get("event")
                values = msg_json.get("props")

                if dest == WS_TAG and event_name != None and values != None:
                    if self.handlers[event_name] != None:
                        handler = self.handlers[event_name]
                        handler(values)


    def send(self, message, room=None, skip_sid=None):
        send_msg = {
            "method" : "emit",
            "event": "message",
            "data" : message,
            "namespace" : "/",
            "room": room,
            "skip_sid" : skip_sid,
            "callback" : None
        }
        #self._publish({'method': 'emit', 'event': event, 'data': data,
        #               'namespace': namespace, 'room': room,
        #               'skip_sid': skip_sid, 'callback': callback})
        self.redis.publish(self.channel, json.dumps(send_msg).encode())

    def register_handler(self, event_name, handler):
        if inspect.isfunction(handler) == True or inspect.ismethod(handler) == True:
            self.handlers[event_name] = handler
