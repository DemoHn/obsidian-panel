__author__ = "Nigshoxiz"

import redis
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class WS_TAG:
    MPW = "MPW"
    CONTROL = "CONTROL"
    CLIENT = "CLIENT"
    APP = "APP"
    FTM = "FTM"

class MessageUserStatusPool(metaclass=Singleton):
    '''
    A pool stores uid and sid data of a message from client indexed by flag.

    data format:
    KEY: <flag>
    VALUE: [<uid>,<sid>,<src>,<dest>]
    '''
    def __init__(self):
        '''
        we use redis database to handle data
        '''
        self.redis = redis.Redis()

    def get(self, flag):
        '''
        :param flag: message flag
        :return: (uid, sid, src, dest)
        '''
        if flag == None:
            return (None, None, None, None)
        _data = self.redis.get(flag)
        if _data == None:
            return (None, None, None, None)

        _obj = _data.decode().split(",")
        uid = _obj[0]
        sid = _obj[1]
        src = _obj[2]
        dest = _obj[3]
        return (uid, sid, src, dest)

    def exists(self, flag):
        if flag == None:
            return False

        if self.redis.get(flag) != None:
            return True
        else:
            return False

    def _set(self, flag, uid, sid, src, dest):
        arr = [uid, sid, src, dest]
        arr_str = ",".join(arr)
        self.redis.set(flag, arr_str.encode())

    def put(self, flag, uid, sid, src, dest):
        self._set(flag, uid, sid, src, dest)

    def update(self, flag,
               uid = None,
               sid = None,
               src = None,
               dest= None):
        '''
        update storage data
        :return:
        '''
        _uid, _sid, _src, _dest = self.get(flag)

        if uid == None:
            uid = _uid
        if sid == None:
            sid = _sid
        if src == None:
            src = _src
        if dest == None:
            dest = _dest

        self._set(flag, uid, sid, src, dest)

    def delete(self, flag):
        self.redis.delete(flag)

from .proxy import MessageQueueProxy
from .event_handler import MessageEventHandler

