from .status_pool import MessageUserStatusPool
from . import Singleton
class MessageEventHandler(metaclass=Singleton):
    __prefix__ = None

    def __init__(self):
        self.pool = MessageUserStatusPool()
        self.proxy = None
        if self.__class__.__prefix__ == None:
            raise NotImplementedError("Prefix not set!")

    def _set_proxy(self, proxy):
        self.proxy = proxy