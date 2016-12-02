from app.tools.mq_proxy import MessageQueueProxy, MessageEventHandler

class AppEventHandler(MessageEventHandler):
    __prefix__ = "app"

    def __init__(self):
        MessageEventHandler.__init__(self)
