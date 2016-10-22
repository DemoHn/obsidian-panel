from app import db
from app.utils import WS_TAG
from app import MessageQueueProxy
import inspect

class AppEvents(object):
    '''
    method name:
    just replace "." into "233" (because python doesn't allow dot included as method's name)
    '''
    def __init__(self):
        self.proxy = MessageQueueProxy.getInstance()

        methods_dict = AppEvents.__dict__
        # register all methods into proxy
        for method_name in methods_dict:
            try:
                # to filter python's internal method (magical method)
                if method_name.find("__") != 0:
                    method = methods_dict[method_name]
                    event_name = method_name.replace("233",".")

                    self.proxy.register_handler(event_name, method)
            except:
                continue

    def process233get_instance_status233callback(self):
        pass

