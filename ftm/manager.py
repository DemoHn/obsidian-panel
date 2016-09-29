__author__ = "Nigshoxiz"

from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer
from app.utils import salt

import threading
from multiprocessing import Process, Manager
import socket
import hashlib
import os

class MD5Authorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        hash = hashlib.md5(password.encode('utf-8') + salt).hexdigest()
        try:
            if self.user_table[username]['pwd'] != hash:
                raise KeyError
        except KeyError:
            raise AuthenticationFailed

class ServerThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)

        self.manager = FTPManager(port)
        address = ("127.0.0.1", self.manager.listening_port)
        self.manager.server = FTPServer(address, self.manager.handler)

    def run(self):
        self.manager.server.serve_forever()

class FTPManager(object):

    def __init__(self, port):
        self.handler = FTPHandler
        self.authorizer = MD5Authorizer()
        self.handler.authorizer = self.authorizer
        self.server = None
        self.login_msg = "Login Successful"
        self.quit_msg  = "GoodBye"
        self.listening_port = port

        self.server_process = None

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
        address = ("127.0.0.1", self.listening_port)
        self.server = FTPServer(address, self.handler)

        self.server.serve_forever(blocking=True)
