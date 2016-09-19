__author__ = "Nigshoxiz"

from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer
from app.utils import salt

import threading
import hashlib

class MD5Authorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        hash = hashlib.md5(password.encode('utf-8') + salt).hexdigest()
        try:
            if self.user_table[username]['pwd'] != hash:
                raise KeyError
        except KeyError:
            raise AuthenticationFailed

class FTPManager(object):
    def __init__(self, listen_port):
        self.handler = FTPHandler
        self.authorizer = MD5Authorizer()
        self.handler.authorizer = self.authorizer

        self.listening_port = listen_port

        self.login_msg = "Login Successful"
        self.quit_msg  = "GoodBye"
        pass

    def add_user(self, username, password, working_dir, permission="elradfmw"):
        hash = hashlib.md5(password.encode('utf-8') + salt).hexdigest()
        self.authorizer.add_user(username, hash, working_dir,
                                 perm = permission,
                                 msg_login=self.login_msg,
                                 msg_quit=self.quit_msg)

    def remove_user(self, username):
        self.authorizer.remove_user(username)

    def set_welcome_banner(self, msg):
        self.login_msg = msg

    def set_quit_banner(self, msg):
        self.quit_msg = msg

    def launch(self):
        def _launch_server():
            address = ("127.0.0.1", self.listening_port)
            server = ThreadedFTPServer(address, self.handler)
            server.serve_forever()

        t = threading.Thread(target=_launch_server)
        t.daemon = True
        t.start()
