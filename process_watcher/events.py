from app import db
from app.model import Users, UserToken, ServerInstance
from app.controller.global_config import GlobalConfig

from . import SERVER_STATE
from .mq_proxy import MessageQueueProxy
from .watchdog import Watchdog

import inspect
class WatcherEvents(object):
    '''
    This class handles control events from other side (app,websocket and so on).
    Of course, since the watcher is an independent process, we use message queue
    to control it.
    DON'T FORGET SEND AN 'ACK' message after finishing!
    '''

    def __init__(self):
        self.watcher = Watchdog.getWDInstance()
        self.proxy   = MessageQueueProxy.getInstance()

        events = (
            "get_instance_status",
            "get_active_instances",
            "get_instance_log",
            "add_instance",
            "remove_instance",
            "start_instance",
            "stop_instance"
        )

        # register handler
        for e in events:
            try:
                _method = getattr(self, e)
                if inspect.ismethod(_method):
                    event_name = "process.%s" % e
                    self.proxy.register_handler(event_name, _method)
            except:
                continue

        pass

    def get_instance_status(self, values):
        '''
        DESCRIPTION: get all instances registered on the process pool.

        EVENT NAME: process.get_instance_status

        :param values: {'inst_id': "all"} | {"inst_id" : <inst_id>}
        :return: {
            "status" : "success",
            "inst": [{
                "inst_id" : <inst_id>,
                "port" : <port>,
                "current_player" : <player num>,
                "RAM": <allocated RAM>,
                "status" : SERVER_STATE.HALT | RUNNING | STARTING
            }]
        } OR
        {
            "status" : "error"
        }
        '''
        self.proxy.send("process.get_instance_status.callback", "CLIENT", {"inst_id" : 1}, uid = 1)
        pass

    def get_active_instances(self, values):
        '''
        DESCRIPTION: return all active instances (STARING | RUNNING)

        EVENT NAME: process.get_active_instances

        :param values: {'inst_id': <inst_id> }
        :return:
        {
            "status" : "success",
            "inst": {
                "inst_id" : <inst_id>,
                "port" : <port>,
                "current_player" : <player num>,
                "RAM": <allocated RAM>
                # status must be r
            }
        }
        OR
        {
            "status" : "error"
        }
        '''
        pass

    def get_instance_log(self, values):
        '''
        DESCRIPTION: get instance log (all log)

        EVENT NAME: process.get_instance_log

        :param values: {"inst_id" : <inst_id>}
        :return:
        {
            "inst_id" : <inst_id>,
            "log" : [<Array>]
        }
        '''
        pass

    def add_instance(self, values):
        '''
        DESCRIPTION: add instance. But not activate it immediately.

        EVENT_NAME: process.add_instance
        :param values:
        :return:
        '''
        pass

    def remove_instance(self, values):
        '''
        DESCRIPTION: remove instance from process pool.

        EVENT_NAME: process.remove_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        pass

    def start_instance(self, values):
        '''
        DESCRIPTION: start a instance.

        EVENT_NAME: process.start_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        pass

    def stop_instance(self, values):
        '''
        DESCRIPTION: stop a instance.

        EVENT_NAME: process.stop_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        pass

class EventSender(object):
    '''
    EventSender takes responsibility for sending instance events to
    websocket client (in order notifying the browser).

    Actually, it has been initialized when watcher starts to launch.
    (see launch.py for details)
    '''
    def __init__(self, watcher_obj):
        self.add_hook_func = watcher_obj.add_hook
        self.watcher_obj   = watcher_obj
        _names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout",
                  "inst_player_change","inst_memory_change")

        gc = GlobalConfig.getInstance()

        if gc.getInitFlag() == True:
            # add hook function
            for item in _names:
                _method = getattr(self, "on_%s" % item)
                self.add_hook_func(item, _method)

            self.conn = MessageQueueProxy.getInstance()
            # KEY : <inst_id>
            # VALUE : <uid>
            self._inst_uid_cache = {}
            # refresh cache the first time
            self._get_uid_from_inst_id(0)

    def _get_uid_from_inst_id(self, inst_id):
        inst_key = "inst_%s" % inst_id
        if self._inst_uid_cache.get(inst_key) != None:
            return self._inst_uid_cache.get(inst_key)
        else:
            # read from database
            owners = db.session.query(ServerInstance).all()
            for serv_inst in owners:
                inst_key = "inst_%s" % serv_inst.inst_id
                self._inst_uid_cache[inst_key] = serv_inst.owner_id

            return self._inst_uid_cache.get(inst_key)

    # event name : inst_event
    def _send(self, inst_id, event, value):
        values = {
            "inst_id" : inst_id,
            "value" : value
        }
        uid = self._get_uid_from_inst_id(inst_id)
        self.conn.send(event, "CLIENT", values, uid = uid)

    # event listeners
    def on_inst_starting(self, inst_id, p):
        self._send(inst_id, "status_change", SERVER_STATE.STARTING)

    def on_inst_running(self, inst_id, p):
        self._send(inst_id, "status_change", SERVER_STATE.RUNNING)

    def on_log_update(self, inst_id, p):
        log_str = p
        if len(log_str) > 0: # prevent sending empty string
            self._send(inst_id, "log_update", log_str)

    def on_connection_lost(self, inst_id, p):
        pass

    def on_inst_terminate(self, inst_id, p):
        self._send(inst_id, "status_change", SERVER_STATE.HALT)

    def on_inst_player_login(self, inst_id ,p):
        inst_obj = self.watcher_obj.just_get(inst_id)
        if inst_obj != None:
            players_num = inst_obj.get("current_player")
            self._send(inst_id, "player_change", players_num)

    def on_inst_player_logout(self, inst_id, p):
        inst_obj = self.watcher_obj.just_get(inst_id)
        if inst_obj != None:
            players_num = inst_obj.get("current_player")
            self._send(inst_id, "player_change", players_num)


    def on_inst_player_change(self, inst_id, p):
        online, total = p
        self._send(inst_id, "player_change", online)
        #print("<inst %s> online player: %s" % (inst_id, online))

    def on_inst_memory_change(self, inst_id, p):
        mem = p
        self._send(inst_id, "memory_change", mem)
        #print("<inst %s> memory : %s" % (inst_id, mem))
