from app import socketio
from .event_loop import EventLoop
# import python library
import logging
logger = logging.getLogger("ob_panel")

class SERVER_STATE(object):
    HALT = 0
    STARTING = 1
    RUNNING = 2

event_loop = EventLoop.getInstance()

from .watchdog import Watchdog
watcher = Watchdog.getWDInstance()