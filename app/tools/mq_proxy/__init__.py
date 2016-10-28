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

from .status_pool import MessageUserStatusPool
from .proxy import MessageQueueProxy
from .event_handler import MessageEventHandler

