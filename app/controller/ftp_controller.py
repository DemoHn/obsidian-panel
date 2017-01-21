from app.model import FTPAccount, Users
from app.controller.sys_process import SystemProcessClient
from app.tools.mq_proxy import WS_TAG
from app import db, proxy
from app.utils import salt
import hashlib

class FTPController:
    def __init__(self):
        pass

    def create_account(self, uid, login_username, inst_id, ftp_password = None):
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
                default_password = True
                _ftp_hash = None
            else:
                default_password = False
                _ftp_hash = hashlib.md5(ftp_password.encode('utf-8') + salt).hexdigest()
            account = FTPAccount(
                username = login_username,
                hash = _ftp_hash,
                inst_id = inst_id,
                owner_id = uid,
                default_password = default_password
            )

            db.session.add(account)
            db.session.commit()

        self.update_user()

    def update_user(self):
        proxy.send("ftp.update_users", {}, WS_TAG.FTM, reply=False)
