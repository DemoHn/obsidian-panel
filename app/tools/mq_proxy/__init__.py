__author__ = "Nigshoxiz"

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SingletonP(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        TAG_NAME = args[0]
        if TAG_NAME not in cls._instances:
            cls._instances[TAG_NAME] = super(SingletonP, cls).__call__(*args, **kwargs)
        return cls._instances[TAG_NAME]

class WS_TAG:
    MPW = "MPW"
    CLIENT = "CLIENT"
    APP = "APP"
    FTM = "FTM"
    TSR = "TSR"
    _TEST_RECV = "_TEST_RECV"
    _TEST_SEND = "_TEST_SEND"

from .status_pool import MessageUserStatusPool
from .proxy import MessageQueueProxy
from .event_handler import MessageEventHandler
