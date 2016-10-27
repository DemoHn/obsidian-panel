from app import db
from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy
from app.model import ServerInstance, JavaBinary, ServerCORE

import os
import math

class ProcessEventHandler(MessageEventHandler):
    __prefix__ = "process"

    def __init__(self):
        # denote message proxy for sending message
        # Don't worry, it's a singleton class
        self.proxy = MessageQueueProxy(WS_TAG.CONTROL)
        MessageEventHandler.__init__(self)

    def _test(self, flag, values):
        self.proxy.send(flag, "process._test", values, WS_TAG.MPW)

    def broadcast(self, flag, values):
        # broadcast data to multiple clients
        
        pass
