__author__ = "Nigshoxiz"
from .server import sio, start_websocket_server

from ob_logger import Logger
logger = Logger("WS", debug=True)
class PRIVILEGES:
    NONE = 0x0000
    INST_OWNER = 0x0001
    ROOT_USER = 0x0100

