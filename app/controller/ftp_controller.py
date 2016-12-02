from app.model import FTPAccount, Users
from app.controller.sys_process import SystemProcessClient
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG
from app import db
from app.utils import salt
import hashlib

class FTPController:
    # 「大柠乐」计数器
    # This counter is used to count how many times an event is emitted.
    # This is used for preventing forked processes sending one event at the same time.
    DA_LING_LE_COUNTER = 0
    def __init__(self):
        pass

    def create_account(self, uid, login_username, working_dir, ftp_password = None):
        '''
        by default, when a new instance was created, a FTP
        account for this instance will be also created too.
        2016-10-18 WARNING: Currently, we have to restart the whole
        ftp server to make changes on account affective.

        :return:
        '''
        user = db.session.query(Users).filter(Users.id == uid).first()
        if user == None:
            raise ValueError("No such user!")
        else:
            if ftp_password == None:
                _ftp_hash = user.hash
            else:
                _ftp_hash = hashlib.md5(ftp_password.encode('utf-8') + salt).hexdigest()
            account = FTPAccount(
                username = login_username,
                hash = _ftp_hash,
                working_dir = working_dir,
                owner_id = uid
            )

            db.session.add(account)
            db.session.commit()

        #self.restart_ftp()
        self.update_user()

    def _restart_ftp(self):
        client = SystemProcessClient()
        client.send_restart_cmd("ftp", waiting=True)

    def update_user(self):
        values = {}
        proxy = MessageQueueProxy(WS_TAG.APP)
        proxy.send("up_usr_%s" % FTPController.DA_LING_LE_COUNTER, "ftp.update_users", values, WS_TAG.FTM)
        FTPController.DA_LING_LE_COUNTER += 1