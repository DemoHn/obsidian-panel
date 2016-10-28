from .status_pool import MessageUserStatusPool
from . import Singleton
class MessageEventHandler(metaclass=Singleton):
    __prefix__ = None

    def __init__(self):
        self.pool = MessageUserStatusPool()
        if self.__class__.__prefix__ == None:
            raise Exception("Prefix not set!")