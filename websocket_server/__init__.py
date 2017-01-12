__author__ = "Nigshoxiz"

from ob_logger import Logger
logger = Logger("WS")

class PRIVILEGES:
    NONE = 0x0000
    INST_OWNER = 0x0001
    ROOT_USER = 0x0100

from .server import start_websocket_server, start_zeromq_broker
