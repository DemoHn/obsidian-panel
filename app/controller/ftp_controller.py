from app.model import FTPAccount, Users
from app.controller.sys_process import SystemProcessClient

from app import db

class FTPController:
    def __init__(self):
        pass

    def create_account(self, uid, login_username, working_dir):
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
            user_hash = user.hash

            account = FTPAccount(
                username = login_username,
                hash = user_hash,
                working_dir = working_dir,
                owner_id = uid
            )
            db.session.add(account)
            db.session.commit()

        # TODO : not restart ftp anymore!
        self.restart_ftp()

    def restart_ftp(self):
        client = SystemProcessClient()
        client.send_restart_cmd("ftp", waiting=True)
