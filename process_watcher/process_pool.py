__author__ = "Nigshoxiz"

from . import Singleton
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
        self._proc_pool = {}
        """
        EventLoop Active Handle Count
        This number counts how many active instances are running,
        i.e. handles that required event loop to monitor.

        When Active Count = 0, that means no process needs to monitor.
        There's no need to execute `self._loop.run()`
        """
        self._active_count = 0

    def add(self, inst_id, val):
        self._proc_pool[inst_id] = val

    def get(self, inst_id):
        return self._proc_pool.get(inst_id)

    def get_info(self, inst_id):
        if self._proc_pool.get(inst_id) != None:
            return self._proc_pool.get(inst_id).get("info")

    def get_proc(self, inst_id):
        if self._proc_pool.get(inst_id) != None:
            return self._proc_pool.get(inst_id).get("proc")

    def get_daemon(self, inst_id):
        if self._proc_pool.get(inst_id) != None:
            return self._proc_pool.get(inst_id).get("daemon")

    def get_status(self, inst_id):
        if self._proc_pool.get(inst_id) != None:
            return self._proc_pool.get(inst_id).get("status")

    def get_config(self, inst_id):
        if self._proc_pool.get(inst_id) != None:
            return self._proc_pool.get(inst_id).get("config")
    # set methods
    def set(self, inst_id, key, val):
        if self._proc_pool.get(inst_id) != None:
            if key in ("config", "info", "proc", "daemon","status"):
                self._proc_pool.get(inst_id)[key] = val

    def set_info(self, inst_id, info):
        if self._proc_pool.get(inst_id) != None:
            self._proc_pool.get(inst_id)["info"] = info

    def set_proc(self, inst_id, proc):
        if self._proc_pool.get(inst_id) != None:
            self._proc_pool.get(inst_id)["proc"] = proc

    def seet_daemon(self, inst_id, daemon):
        if self._proc_pool.get(inst_id) != None:
            self._proc_pool.get(inst_id)["daemon"] = daemon

    def set_status(self, inst_id, status):
        if self._proc_pool.get(inst_id) != None:
            self._proc_pool.get(inst_id)["status"] = status

    def set_config(self, inst_id, mc_w_config):
        if self._proc_pool.get(inst_id) != None:
            self._proc_pool.get(inst_id)["config"] = mc_w_config
    # active count
    def get_active_count(self):
        return self._active_count

    # incr and decr active count
    def incr_active_count(self):
        self._active_count += 1

    def decr_active_count(self):
        self._active_count -= 1