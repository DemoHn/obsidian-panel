import logging
import inspect

logger = logging.getLogger("ob_panel")

class InstanceEventEmitter(object):
    '''
    emit websocket on some events
    '''
    def __init__(self, add_hook_func):
        self.add_hook_func = add_hook_func

        _names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout", "inst_player_change")
        # add hook function
        for item in _names:
            _method = getattr(self, "on_%s" % item)
            self.add_hook_func(item, _method)

    def on_inst_starting(self, inst_id, p):
        print("<inst %s> start initialize" % inst_id)
        pass

    def on_inst_running(self, inst_id, p):
        print("<inst %s> start running. Time %s" % (inst_id, p))
        pass

    def on_log_update(self, inst_id, p):
        print(p)
        pass

    def on_connection_lost(self, inst_id, p):
        pass

    def on_inst_terminate(self, inst_id, p):
        print("<inst %s> stopped!" % inst_id)
        pass

    def on_inst_player_login(self, inst_id ,p):
        pass

    def on_inst_player_logout(self, inst_id, p):
        pass

    def on_inst_player_change(self, inst_id, p):
        pass