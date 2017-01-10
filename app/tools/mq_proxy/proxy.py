__author__ = "Nigshoxiz"

import zmq, inspect, threading, time, zmq, json
from uuid import uuid4
from . import Singleton, WS_TAG, MessageUserStatusPool
from .event_handler import MessageEventHandler
import traceback

# logging system
from ob_logger import Logger
logger = Logger("MsgQ", debug=True)

class MessageQueueProxy():
#class MessageQueueProxy(metaclass=Singleton):
    '''
    What is a .. Message Queue Proxy?
    A message queue proxy takes responsibility for receiving message from message queue
    and send message to it.
    Because we use a standalone websocket server, we use message queue to delegate
    websocket server to send websocket message, instead of sending message directly.
    '''
    TAGS = WS_TAG
    def __init__(self, tag, router_port=852):
        self.ws_tag = tag
        self.context = zmq.Context()

        self.sock_send = None

        self.router_port = router_port

        self.handlers = {}

        # bind to zeromq router
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
        # init recv socket
        self.sock_recv = self.context.socket(zmq.DEALER)
        self.sock_recv.setsockopt_string(zmq.IDENTITY, self.ws_tag)
        self.sock_recv.connect("tcp://localhost:%s" % self.router_port)

        while True:
            try:
                _msg = self.sock_recv.recv()
            except:
                # timeout
                logger.error(traceback.format_exc())
                continue

            try:
                msg_json = json.loads(_msg.decode())
                flag = self._get_flag(msg_json.get("flag"))
                # check if available
                event_name = msg_json.get("event")
                values = msg_json.get("props")
                source = msg_json.get("_src")

                if event_name != None and values != None:
                    if self.handlers.get(event_name) != None:
                        handler = self.handlers.get(event_name)
                        rtn_status = {
                            "status" : "success",
                            "data" : None,
                            "_dest" : source
                        }

                        # send back data
                        try:
                            rtn_data = handler(flag, values)
                            rtn_status["data"] = rtn_data
                            self.sock_recv.send(json.dumps(rtn_status).encode())
                        except:
                            logger.debug(traceback.format_exc())
                            rtn_status["status"] = "error"
                            self.sock_recv.send(json.dumps(rtn_status).encode())
                else:
                    # jsut drop it
                    pass
            except:
                logger.error(traceback.format_exc())

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

    def send(self, event, values, dest, _src=None):
        '''
        :param event:
        :param values:
        :param dest: the destination of message. choices:
         WS_TAG.CLIENT | WS_TAG.MPW and so on
        :return:
        '''
                # init send socket
        if self.sock_send == None:
            self.sock_send = self.context.socket(zmq.DEALER)
            self.sock_send.setsockopt_string(zmq.IDENTITY, self.ws_tag)
            self.sock_send.setsockopt(zmq.RCVTIMEO, 3000) # 5 sec timeout
            self.sock_send.connect("tcp://localhost:%s" % self.router_port)

        if _src == None:
            _src = self.ws_tag
        _dest = dest

        send_msg = {
            "event" : event,
            "props" : values,
            "_dest" : _dest,
            "_src"  : _src
        }

        self.sock_send.send(json.dumps(send_msg).encode())
        # and receive data...
        try:
            recv_binary = self.sock_send.recv()
        except:
            return None
        # from binary to json object
        try:
            recv_str = recv_binary.decode()
            recv_json = json.loads(recv_str)
            return recv_json
        except:
            return None
        return

    def listen(self, background=True):
        if background:
            t = threading.Thread(target=self._listen)
            t.setDaemon(True)
            t.start()
        else:
            self._listen()

    def terminate(self):
        self.pub_sub.unsubscribe()
