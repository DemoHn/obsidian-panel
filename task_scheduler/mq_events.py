from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy

class TaskEventHandler(MessageEventHandler):

    __prefix__ = "task"
    def __init__(self):
        MessageEventHandler.__init__(self)

    def start_download(self, flag, values):
        pass

    def terminate_download(self, flag, values):
        pass

    def add_background_task(self, flag, values):
        pass
