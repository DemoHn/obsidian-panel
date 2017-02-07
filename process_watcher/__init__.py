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

def start_process_watcher():
    from .mq_events import WatcherEvents
    from .watcher import Watcher
    from app.tools.mq_proxy import WS_TAG, MessageQueueProxy
    from app.utils import is_debug, read_config_yaml

    logger.set_debug(is_debug())
    _config = read_config_yaml()
    router_port = _config['broker']['listen_port']

    proxy = MessageQueueProxy(WS_TAG.MPW, router_port= router_port)
    proxy.register(WatcherEvents)

    logger.info("This is Minecraft Process Watcher.")
    proxy.listen(background=True)

    # start event loop
    watcher = Watcher()
    watcher.launch_loop()
