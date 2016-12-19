from . import logger, Singleton, SERVER_STATE
from .process_pool import MCProcessPool

from app.tools.mq_proxy import WS_TAG, MessageQueueProxy

class MCProcessCallback(metaclass=Singleton):
    def __init__(self):
        self._proc_pool = MCProcessPool()

    # event name : inst_event
    def broadcast(self, inst_id, event_name, value):
        proxy = MessageQueueProxy(WS_TAG.MPW)
        event_prefix = "process"
        event_type = "broadcast"

        _name = "%s.%s" % (event_prefix, event_type)
        values = {
            "inst_id": inst_id,
            "event": event_name,
            "val": value
        }
        _info = self._proc_pool.get_info(inst_id)
        uid   = _info.get_owner()
        proxy.send(None, _name, values, WS_TAG.CONTROL, uid=uid)

    def on_log_update(self, inst_id, pipe, log):
        logger.debug(log)
        pass

    def on_instance_start(self, inst_id):
        self._proc_pool.set_status(inst_id, SERVER_STATE.STARTING)
        pass

    def on_instance_running(self, inst_id):
        pass

    def on_instance_stop(self, inst_id):
        pass

    def on_instance_unexpectedly_exit(self, inst_id):
        pass

    def on_player_login(self, inst_id, player):
        pass

    def on_player_logout(self, inst_id):
        pass

    def on_player_leave(self, inst_id):
        pass

    def on_player_change(self, inst_id, player):
        pass

    def on_memory_change(self, inst_id, memory):
        pass