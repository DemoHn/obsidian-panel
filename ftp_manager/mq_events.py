from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy
from .manager import FTPManager
class FTPAccountEventHandler(MessageEventHandler):

    __prefix__ = "ftp"
    def __init__(self):
        MessageEventHandler.__init__(self)

    def add_account(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)
        manager = FTPManager()
        manager._test_log()
        pass