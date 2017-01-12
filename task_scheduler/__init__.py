from ob_logger import Logger
from .mq_events import TaskEventHandler
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG

logger = Logger("TSR")

def start_task_scheduler(debug=True):
    logger.set_debug(debug)

    proxy = MessageQueueProxy(WS_TAG.TSR)
    proxy.register(TaskEventHandler)
    proxy.listen(background=True)

    logger.info("This is Task Scheduler")
    import time
    # just for test, waiting for apscheduler
    while True:
        time.sleep(1)
