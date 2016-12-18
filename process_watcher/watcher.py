__author__ = "Nigshoxiz"

from . import logger, SERVER_STATE
from .process import MCProcess
from app.controller.global_config import GlobalConfig

import pyuv

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MCProcessPool(metaclass=Singleton):
    def __init__(self):
        """
        Process Pool
        key -> <inst id>
        value -> {
            "config" : MCWrapperConfig(**) | None,
            "status" : {SERVER_STATE.HALT | STARTING | RUNNING},
            "daemon" : MCDaemonManager(**),
            "info"   : MCInstanceInfo(**),
            "proc"   : MCProcess(**)
        }
        """
        self.proc_pool = {}

    def add(self, inst_id, val):
        self.proc_pool[inst_id] = val

    def get(self, inst_id):
        return self.proc_pool.get(inst_id)

class Watcher(metaclass=Singleton):
    def __init__(self):
        self._loop = pyuv.Loop()

        """
        EventLoop Active Handle Count
        This number counts how many active instances are running,
        i.e. handles that required event loop to monitor.

        When Active Count = 0, that means no process needs to monitor.
        There's no need to execute `self._loop.run()`
        """
        self._active_count = 0
        """
        Is Event Loop running?
        If not, and _active_count > 0 (i.e. some processes need loop to handle!)
        Just create a thread execute `loop.run()`
        """
        self._loop_running = False

        self.proc_pool = MCProcessPool()
        pass

    def _init_proc_pool(self):
        gc = GlobalConfig()

        # first, we have to make sure that
        if gc.get("init_super_admin") == True:
            pass

    def launch(self):
        pass
