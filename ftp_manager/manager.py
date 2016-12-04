__author__ = "Nigshoxiz"

from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer
from app.utils import salt
from app.controller.global_config import GlobalConfig

import threading
import hashlib
import traceback

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MD5Authorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        hash = hashlib.md5(password.encode('utf-8') + salt).hexdigest()
        try:
            if self.user_table[username]['pwd'] != hash:
                raise KeyError
        except KeyError:
            raise AuthenticationFailed

class FTPManager(metaclass=Singleton):

    def __init__(self):
        self.handler = FTPHandler
        self.authorizer = MD5Authorizer()
        self.handler.authorizer = self.authorizer
        self.server = None
        self.login_msg = "Login Successful"
        self.quit_msg  = "GoodBye"
        self.listening_port = None

        self.server_process = None
        # read global config
        self._global_config = GlobalConfig.getInstance()

        if self._get_initdb_status():
            self._update_account_data()

    def _get_initdb_status(self):
        if self._global_config.get("init_super_admin") == True:
            return True
        else:
            return False

    def _update_account_data(self):
        db_type = self._global_config.get("db_type")
        data = []
        exec_statement = "SELECT ob_ftp_account.username, " \
                         " ob_ftp_account.default_password," \
                         " ob_ftp_account.hash," \
                         " ob_ftp_account.permission," \
                         " ob_server_instance.inst_dir," \
                         " ob_user.hash" \
                         " FROM ob_ftp_account INNER JOIN ob_server_instance ON ob_server_instance.inst_id = ob_ftp_account.inst_id" \
                         " INNER JOIN ob_user ON ob_ftp_account.owner_id = ob_user.id"
        if self._global_config.get("init_super_admin") == True:
            db_env = self._global_config

            if db_type == "sqlite":
                database_uri = "%s/%s.db" % (db_env.get("sqlite_dir"),
                                                       db_env.get("db_name"))
                conn = None
                try:
                    import sqlite3
                    conn = sqlite3.connect(database_uri)
                    cursor = conn.cursor()
                    cursor.execute(exec_statement)

                    data = cursor.fetchall()
                except:
                    traceback.print_exc()
                finally:
                    if conn != None:
                        conn.close()
            else:
                conn = None
                try:
                    import pymysql
                    conn = pymysql.connect(host=db_env.get("db_mysql_ip"),
                             user= db_env.get("db_mysql_username"),
                             password=db_env.get("db_mysql_password"),
                             db=db_env.get("db_name"),
                             charset='utf8mb4')

                    cursor = conn.cursor()
                    cursor.execute(exec_statement)

                    data = cursor.fetchall()
                except:
                    traceback.print_exc()
                finally:
                    if conn != None:
                        conn.close()
            # connect database server
            # clear user table
            self.authorizer.user_table = {}
            for item in data:
                _username = item[0]
                _default_password = item[1]
                _account_hash = item[2]
                _permission = item[3]
                _work_dir = item[4]
                _user_hash     = item[5]

                _hash = _user_hash
                if _default_password == 0:
                    _hash = _account_hash
                self.add_user(_username, _hash, _work_dir, permission=_permission)
        else:
            # relax, there's nothing to do
            return None

    def add_user(self, username, hash, working_dir, permission="elradfmw"):
        #hash = hashlib.md5(password.encode('utf-8') + salt).hexdigest()
        self.authorizer.add_user(username, hash, working_dir,
                                 perm = permission,
                                 msg_login=self.login_msg,
                                 msg_quit=self.quit_msg)

    def update_user_info(self):
        self._update_account_data()

    def remove_user(self, username):
        self.authorizer.remove_user(username)

    def set_port(self, port):
        self.listening_port = port

    def set_welcome_banner(self, msg):
        self.login_msg = msg

    def set_quit_banner(self, msg):
        self.quit_msg = msg

    def launch(self, background=False):
        def _launch(self):
            address = ("127.0.0.1", self.listening_port)
            self.server = FTPServer(address, self.handler)
            self.server.serve_forever()

        if background:
            t = threading.Thread(target=_launch, args=(self,))
            t.setDaemon(True)
            t.start()
        else:
            _launch(self)