from ob_logger import Logger
from .mq_events import TaskEventHandler
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG

logger = Logger("TSR")

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def start_task_scheduler(debug=True, zmq_port=852):
    logger.set_debug(debug)

    proxy = MessageQueueProxy(WS_TAG.TSR, router_port=zmq_port)
    proxy.register(TaskEventHandler)
    proxy.listen(background=True)

    logger.info("This is Task Scheduler")
    import time
    # just for test, waiting for apscheduler
    while True:
        time.sleep(1)
