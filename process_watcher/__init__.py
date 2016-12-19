# import python library

from ob_logger import Logger
logger = Logger("MPW")

class SERVER_STATE(object):
    HALT = 0
    STARTING = 1
    RUNNING = 2

class PipeNo(object):
    STDIN = 0
    STDOUT = 1
    STDERR = 2

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def start_process_watcher(debug=True):
    logger.set_debug(debug)
#    from .watchdog import Watchdog
    from .mq_events import EventSender, WatcherEvents
    from app.tools.mq_proxy import WS_TAG, MessageQueueProxy

#    watcher = Watchdog.getWDInstance()
#    watcher.launch(hook_class=EventSender)

    proxy = MessageQueueProxy(WS_TAG.MPW)
    proxy.register(WatcherEvents)

    logger.info("This is Minecraft Process Watcher.")
    proxy.listen(background=False)
