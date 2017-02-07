from ob_logger import Logger
from functools import wraps

from app.tools.mq_proxy import MessageQueueProxy, WS_TAG
from apscheduler.schedulers.blocking import BlockingScheduler

from .mq_events import TaskEventHandler

logger = Logger("TSR")

# A dict which stores all timing tasks
# model format:
# <task name>:{
#    "cron" : <cron data>,
#    "kwargs" : <kwargs>,
#    "fn" : <function>
# }
global task_map
task_map = {}

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def register_task(cron_data, kwargs_dict={}):
    def real_function(fn):
        func_name = fn.__name__
        _model = {
            "cron" : cron_data,
            "kwargs" : kwargs_dict,
            "fn" : fn
        }

        task_map[func_name] = _model

    return real_function

def start_task_scheduler():
    from . import tasks
    from app.utils import is_debug, read_config_yaml

    logger.set_debug(is_debug())
    _config = read_config_yaml()
    zmq_port = _config['broker']['listen_port']
    # init proxy
    proxy = MessageQueueProxy(WS_TAG.TSR, router_port=zmq_port)
    proxy.register(TaskEventHandler)
    proxy.listen(background=True)

    logger.info("This is Task Scheduler")

    scheduler = BlockingScheduler()

    # add job
    for task in task_map:
        task_obj = task_map[task]
        cron     = task_map[task]["cron"].split(" ")
        scheduler.add_job(
            func = task_obj["fn"],
            trigger = 'cron',
            kwargs = task_obj["kwargs"],
            # cron data
            year = cron[0],
            month = cron[1],
            day = cron[2],
            week = cron[3],
            day_of_week = cron[4],
            hour = cron[5],
            minute = cron[6],
            second = cron[7]
        )

    scheduler.start()
