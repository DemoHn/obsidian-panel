__author__ = "Nigshoxiz"

from websocket_server.mq_proxy import MessageQueueProxy
import inspect
class Controller(object):
    def __init__(self, prefix=None):
        self.proxy = MessageQueueProxy.getInstance()
        self.prefix = prefix

        self._register()
        pass

    def _register(self):
        # get method dict of child class
        methods_dict = self.__class__.__dict__

        for method_name in methods_dict:
            if method_name.find("__") != 0:
                method = getattr(self, method_name)

                if inspect.isfunction(method) or inspect.ismethod(method):
                    event_name = "%s.%s" % (self.prefix, method_name)
                    #self.proxy.register_handler(event_name, method)
