from app import db
from app.utils import WS_TAG
from app.model import ServerInstance
from app.controller.global_config import GlobalConfig

from . import SERVER_STATE
from .mq_proxy import MessageQueueProxy
from .watchdog import Watchdog

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

        methods_dict = WatcherEvents.__dict__
        # register all methods into proxy
        for method_name in methods_dict:
            try:
                # to filter python's internal method (magical method)
                if method_name.find("__") != 0:
                    method = getattr(self, method_name)
                    event_name = "process.%s" % method_name
                    self.proxy.register_handler(event_name, method)
            except:
                continue

    def get_instance_status(self, flag, values):
        '''
        DESCRIPTION: get all instances of ONE user registered on the process pool.

        EVENT NAME: process.get_instance_status

        :param values: {'_uid': <user_id>}
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

        def _get_status(inst_obj):
            return inst_obj.get_status()

        def _get_owner_uid(inst_id):
            _q = db.session.query(ServerInstance).filter(ServerInstance.inst_id == inst_id).first()
            if _q  == None:
                return None
            else:
                return _q.owner_id

        EVENT_NAME = "process.get_instance_status.callback"
        rtn_data = {
            "status": "success",
            "inst": []
        }
        uid = values.get("_uid")
        sender = values.get("_from")

        if uid == None:
            #rtn_data["status"] = "error"
            return None
            #self.proxy.send(EVENT_NAME, "CLIENT", rtn_data, uid=1)
        pool = self.watcher.proc_pool
        for key in pool:
            _obj = pool[key]
            _model = {
                "inst_id": _obj["inst_id"],
                "port": _obj["port"],
                "current_player": _obj["current_player"],
                "RAM": _obj["RAM"],
                "status": _get_status(_obj["inst"])
            }

            if int(_get_owner_uid(_obj["inst_id"])) == int(uid):
                rtn_data["inst"].append(_model)

        # if the message is sent from browser
        if sender == WS_TAG.CLIENT:
            self.proxy.send(EVENT_NAME, sender,flag, rtn_data, uid=uid)

    def get_active_instances(self, flag, values):
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

        def _get_status(inst_obj):
            return inst_obj.get_status()

        def _get_owner_uid(inst_id):
            _q = db.session.query(ServerInstance).filter(ServerInstance.inst_id == inst_id).first()
            if _q  == None:
                return None
            else:
                return _q.owner_id
        EVENT_NAME = "process.get_active_status.callback"
        uid = values.get("_uid")
        sender = values.get("_from")
        rtn_data = {
            "status": "success",
            "inst": []
        }

        if uid == None:
            return None

        pool = self.watcher.proc_pool
        for key in pool:
            _obj = pool[key]
            _model = {
                "inst_id": _obj["inst_id"],
                "port": _obj["port"],
                "current_player": _obj["current_player"],
                "RAM": _obj["RAM"],
                "status": _get_status(_obj["inst"])
            }

            if _get_status(_obj["inst"]) != SERVER_STATE.HALT and \
                    _get_owner_uid(_obj["inst_id"]) == uid:
                rtn_data["inst"].append(_model)

        if sender == WS_TAG.CLIENT:
            self.proxy.send(EVENT_NAME, WS_TAG.CLIENT, flag, rtn_data, uid=uid)

    def get_instance_log(self, flag, values):
        # TODO
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

    def add_instance(self, flag, values, send_ack=True):
        '''
        DESCRIPTION: add instance. But not activate it immediately.

        EVENT_NAME: process.add_instance
        :param values: {"inst_id": <inst_id>, "port": <port>, "config": <config json>}
        :return:
        '''
        EVENT_NAME = "process.add_instance.callback"

        rtn_data = {
            "status": "success",
            "inst_id": None
        }

        _inst_id = values.get("inst_id")
        _port = values.get("port")
        _config = values.get("config")

        sender = values.get("_from")

        self.watcher.register_instance(_inst_id, _port, _config)
        rtn_data["inst_id"] = _inst_id

        if send_ack:
            # we only recv message from app
            if sender == WS_TAG.APP:
                self.proxy.send(EVENT_NAME, WS_TAG.APP, flag, rtn_data)

    def remove_instance(self, flag, values):
        '''
        DESCRIPTION: remove instance from process pool.

        EVENT_NAME: process.remove_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        EVENT_NAME = "process.remove_instance.callback"

        rtn_data = {
            "status": "success",
            "inst_id": None
        }
        sender = values.get("_from")
        inst_id = values.get("inst_id")

        self.watcher.del_instance(inst_id)
        rtn_data["inst_id"] = inst_id

        if sender == WS_TAG.APP:
            self.proxy.send(EVENT_NAME, WS_TAG.APP, flag, rtn_data)
        pass

    def start_instance(self, flag, values, send_ack=True):
        '''
        DESCRIPTION: start a instance.

        EVENT_NAME: process.start_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        EVENT_NAME = "process.start_instance.callback"

        rtn_data = {
            "status": "success",
            "inst_id": None
        }
        sender = values.get("_from")
        inst_id = values.get("inst_id")
        self.watcher.start_instance(inst_id)
        rtn_data["inst_id"] = inst_id

        if send_ack:
            if sender == WS_TAG.APP:
                self.proxy.send(EVENT_NAME, WS_TAG.APP, flag, rtn_data)
            elif sender == WS_TAG.CLIENT:
                uid = values.get("_uid")
                if uid == None:
                    return None
                else:
                    self.proxy.send(EVENT_NAME, WS_TAG.CLIENT, flag, rtn_data, uid=uid)

    def stop_instance(self, flag, values, send_ack=True):
        '''
        DESCRIPTION: stop a instance.

        EVENT_NAME: process.stop_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        EVENT_NAME = "process.stop_instance.callback"

        rtn_data = {
            "status": "success",
            "inst_id": None
        }
        sender = values.get("_from")
        inst_id = values.get("inst_id")

        self.watcher.stop_instance(inst_id)
        rtn_data["inst_id"] = inst_id

        if send_ack:
            if sender == WS_TAG.APP:
                self.proxy.send(EVENT_NAME, WS_TAG.APP, flag, rtn_data)
            elif sender == WS_TAG.CLIENT:
                uid = values.get("_uid")
                if uid == None:
                    return None
                else:
                    self.proxy.send(EVENT_NAME, WS_TAG.CLIENT, flag, rtn_data, uid=uid)

    def _test(self, flag, values):
        print("test data : %s" % values)

    def add_and_start(self, flag, values):
        self.add_instance(flag, values,send_ack=False)
        self.start_instance(flag, values,send_ack=False)


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

            self.proxy = MessageQueueProxy.getInstance()
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
    def send(self, inst_id, event_name, value):
        event_prefix = "process"
        event_type   = "notification"

        event_name   = "%s.%s.%s" % (event_prefix, event_name, event_type)
        values = {
            "inst_id" : inst_id,
            "val" : value
        }
        uid = self._get_uid_from_inst_id(inst_id)
        self.proxy.send(event_name, WS_TAG.CLIENT, values, uid = uid)

    # event listeners
    def on_inst_starting(self, inst_id, p):
        self.send(inst_id, "status_change", SERVER_STATE.STARTING)

    def on_inst_running(self, inst_id, p):
        self.send(inst_id, "status_change", SERVER_STATE.RUNNING)

    def on_log_update(self, inst_id, p):
        log_str = p
        if len(log_str) > 0: # prevent sending empty string
            self.send(inst_id, "log_update", log_str)

    def on_connection_lost(self, inst_id, p):
        pass

    def on_inst_terminate(self, inst_id, p):
        self.send(inst_id, "status_change", SERVER_STATE.HALT)

    def on_inst_player_login(self, inst_id ,p):
        inst_obj = self.watcher_obj.just_get(inst_id)
        if inst_obj != None:
            players_num = inst_obj.get("current_player")
            self.send(inst_id, "player_change", players_num)

    def on_inst_player_logout(self, inst_id, p):
        inst_obj = self.watcher_obj.just_get(inst_id)
        if inst_obj != None:
            players_num = inst_obj.get("current_player")
            self.send(inst_id, "player_change", players_num)


    def on_inst_player_change(self, inst_id, p):
        online, total = p
        self.send(inst_id, "player_change", online)
        #print("<inst %s> online player: %s" % (inst_id, online))

    def on_inst_memory_change(self, inst_id, p):
        mem = p
        self.send(inst_id, "memory_change", mem)
        #print("<inst %s> memory : %s" % (inst_id, mem))
