__author__ = "Nigshoxiz"

from ob_logger import Logger
from app.utils import is_debug

logger = Logger("MsgQ", debug = is_debug())

class PRIVILEGES:
    NONE = 0x0000
    INST_OWNER = 0x0001
    ROOT_USER = 0x0100

from .server import start_zeromq_broker
