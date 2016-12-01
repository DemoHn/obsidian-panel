from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy
from .manager import FTPManager
class FTPAccountEventHandler(MessageEventHandler):

    __prefix__ = "ftp"
    def __init__(self):
        MessageEventHandler.__init__(self)

    def add_account(self, flag, values):
        '''
        :param flag:
        :param values:
         {
             "username" : <username>,
             "hash" : ****,
             "working_dir" : ****
         }
        :return:
        '''
        uid, sid, src, dest = self.pool.get(flag)
        if src == WS_TAG.APP:
            manager = FTPManager()
            manager.add_user(values["username"], values["hash"], values["workding_dir"])

    def remove_account(self, flag, values):
        # TODO
        uid, sid, src, dest = self.pool.get(flag)

    def update_users(self, flag, values):
        '''
        update user info from data table `ob_ftp_account`.
        :param flag:
        :param values:
        :return:
        '''
        uid, sid, src, dest = self.pool.get(flag)
        # only accept data from APP
        if src == WS_TAG.APP:
            manager = FTPManager()
            manager.update_user_info()