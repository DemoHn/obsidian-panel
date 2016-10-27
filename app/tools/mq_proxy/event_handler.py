from .status_pool import MessageUserStatusPool
class MessageEventHandler(object):
    __prefix__ = None

    def __init__(self):
        self.pool = MessageUserStatusPool()
        if self.__class__.__prefix__ == None:
            raise Exception("Prefix not set!")