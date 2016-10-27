from app import db
from app.tools.mq_proxy import WS_TAG, MessageEventHandler
from app.model import ServerInstance, JavaBinary, ServerCORE

import os
import math

class ProcessEventHandler(MessageEventHandler):
    __prefix__ = "process"

    def _test(self, flag, values):
        print("[process event handler] Roger")
