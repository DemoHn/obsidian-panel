__author__ = "Nigshoxiz"

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
        self.pool = {}

    def get(self, flag):
        '''
        :param flag: message flag
        :return: (uid, sid, src, dest)
        '''
        if flag == None:
            return (None, None, None, None)
        _obj = self.pool.get(flag)
        if _obj == None:
            return (None, None, None, None)

        uid = _obj[0]
        sid = _obj[1]
        src = _obj[2]
        dest = _obj[3]
        return (uid, sid, src, dest)

    def exists(self, flag):
        if flag == None:
            return False

        if self.pool.get(flag) != None:
            return True
        else:
            return False

    def put(self, flag, uid, sid, src, dest):
        arr = []
        arr[0] = uid
        arr[1] = sid
        arr[2] = src
        arr[3] = dest
        self.pool[flag] = arr

    def update(self, flag,
               uid = None,
               sid = None,
               src = None,
               dest= None):
        '''
        update storage data
        :return:
        '''
        _obj = self.pool.get(flag)
        if _obj == None:
            return None

        if uid != None:
            _obj[0] = uid
        if sid != None:
            _obj[1] = sid
        if src != None:
            _obj[2] = src
        if dest != None:
            _obj[3] = dest

    def delete(self, flag):
        del self.pool[flag]
