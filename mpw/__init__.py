# import python library
import logging
logger = logging.getLogger("ob_panel")

class SERVER_STATE(object):
    HALT = 0
    STARTING = 1
    RUNNING = 2