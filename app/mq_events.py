from app.utils import WS_TAG
from app.mq_proxy import MessageQueueProxy
import inspect
import os
class AppEvents(object):
    '''
    method name:
    just replace "." into "233" (because python doesn't allow dot included as method's name)
    e.g. : "process.test" --> "process233test"

    method params:
    (flag, value)
    '''

    # NOTICE : when other side send a message to the queue, the queue will
    # BROADCAST it to every process of the App!
    # Thus, try to avoid send message to App!
    def __init__(self):
        self.proxy = MessageQueueProxy.getInstance()

        methods_dict = AppEvents.__dict__
        # register all methods into proxy
        for method_name in methods_dict:
            try:
                # to filter python's internal method (magical method)
                if method_name.find("__") != 0:
                    method = getattr(self, method_name)
                    event_name = method_name.replace("233",".")
                    self.proxy.register_handler(event_name, method)
            except:
                continue

    def process233get_instance_status233callback(self):
        pass

    def process233test(self, flag, values):
        print("pid=%s content=%s flag=%s" % (os.getpid(), values, flag))

