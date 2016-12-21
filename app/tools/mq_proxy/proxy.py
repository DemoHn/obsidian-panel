__author__ = "Nigshoxiz"

import redis, pickle, inspect, threading, time
from uuid import uuid4
from . import Singleton, WS_TAG, MessageUserStatusPool
from .event_handler import MessageEventHandler
import traceback

# logging system
from ob_logger import Logger
logger = Logger("MsgQ", debug=True)
class MessageQueueProxy(metaclass=Singleton):
    '''
    What is a .. Message Queue Proxy?
    A message queue proxy takes responsibility for receiving message from message queue
    and send message to it.
    Because we use a standalone websocket server, we use message queue to delegate
    websocket server to send websocket message, instead of sending message directly.
    '''
    TAGS = WS_TAG
    def __init__(self, tag):
        self.redis = redis.Redis()
        self.pub_sub = self.redis.pubsub()
        self.ws_tag = tag

        self.channel = "control"

        self.pub_sub.subscribe(self.channel)
        # don't be afraid of initializing this class directly
        # It's a singleton class
        self.pool = MessageUserStatusPool()
        self.handlers = {}

        # for send_sync()
        self._sync_event = {}
    def _get_flag(self, flag):
        '''
        get flag. If flag is None, it will return an automatically generated uuid-like
        flag.
        :param flag:
        :return:
        '''
        if flag == None:
            return uuid4()
        else:
            return flag

    def _listen(self):
        channel = self.channel.encode()
        for msg in self.pub_sub.listen():
            if msg["type"] == "message" and msg["channel"] == channel:
                msg_json = pickle.loads(msg['data'])
                flag = self._get_flag(msg_json.get("flag"))
                # check if available
                event_name = msg_json.get("event")
                values = msg_json.get("props")
                uid,sid,src,dest = self.pool.get(flag)

                if dest == self.ws_tag and event_name != None and values != None:
                    # set sync dict
                    if self._sync_event.get(event_name) == "WAITING":
                        self._sync_event[event_name] = values

                    if self.handlers.get(event_name) != None:
                        handler = self.handlers.get(event_name)
                        try:
                            handler(flag, values)
                        except:
                            logger.debug(traceback.format_exc())

    def _register_handler(self, event_name, handler):
        if inspect.ismethod(handler):
            self.handlers[event_name] = handler

    def register(self, cls):
        _instance = cls()
        if not issubclass(cls, MessageEventHandler):
            raise ValueError("Not a child class of MessageEventHandler!")

        methods_dict = cls.__dict__
        # register proxy (which is MessageQueueProxy itself, of course)
        _instance._set_proxy(self)
        # register all methods into proxy
        for method_name in methods_dict:
            try:
                # to filter python's internal method (magical method)
                if method_name.find("__") != 0 and method_name.find("_"+cls.__name__) != 0:
                    method = getattr(_instance, method_name)
                    event_name = "%s.%s" % (cls.__prefix__, method_name)
                    self._register_handler(event_name, method)
            except:
                continue
        pass

    def send(self, flag, event, values, dest, uid=None, sid=None, _src=None):
        '''

        :param flag: just flag
        :param event:
        :param values:
        :param dest: the destination of message. choices:
         WS_TAG.CLIENT | WS_TAG.MPW and so on
        :return:
        '''
        if flag == None:
            flag = self._get_flag(flag)

        send_msg = {
            "event" : event,
            "props" : values,
            "flag"  : flag
        }

        if _src == None:
            _src = self.ws_tag

        _dest = dest
        if self.pool.exists(flag):
            self.pool.update(flag, src=_src, dest=_dest)
        else:
            self.pool.put(flag, uid, sid, _src, _dest)
        self.redis.publish(self.channel, pickle.dumps(send_msg))

    def listen(self, background=True):
        if background:
            t = threading.Thread(target=self._listen)
            t.setDaemon(True)
            t.start()
        else:
            self._listen()

    def terminate(self):
        self.pub_sub.unsubscribe()
