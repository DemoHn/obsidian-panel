from app import db
from app.model import ServerInstance
from app.controller.global_config import GlobalConfig
from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy, Singleton

from . import SERVER_STATE
from .watcher import Watcher

import time

class WatcherEvents(MessageEventHandler):
    '''
    This class handles control events from other side (app,websocket and so on).
    Of course, since the watcher is an independent process, we use message queue
    to control it.
    '''
    __prefix__ = "process"
    def __init__(self):
        self.watcher = Watcher()
        MessageEventHandler.__init__(self)

    def get_instance_status(self, flag, values):
        '''
        DESCRIPTION: get instance info by instance id.

        EVENT NAME: process.get_instance_status

        :param values: {'inst_id': <user_id>}
        :return: {
            "status" : "success",
            "inst": {
                "inst_id" : <inst_id>,
                "current_player" : <player num>,
                "total_player" : <total player>,
                "RAM": <allocated RAM>,
                "total_RAM" : <total RAM>,
                "status" : SERVER_STATE.HALT | RUNNING | STARTING
            }
        } OR
        {
            "status" : "error"
        }
        '''
        # ===== TODO TODO TODO =====
        uid, sid, src, dest = self.pool.get(flag)
        EVENT_NAME = "process.response"

        def _get_status(inst_obj):
            return inst_obj.get_status()

        def _get_owner_uid(inst_id):
            _q = db.session.query(ServerInstance).filter(ServerInstance.inst_id == int(inst_id)).first()
            if _q  == None:
                return None
            else:
                return _q.owner_id

        inst_id = int(values.get("inst_id"))

        if inst_id == None:
            rtn_data = {
                "status" : "error",
                "inst_id" : inst_id,
                "val" : "INST_ID_NULL"
            }
            # send error msg
            self.proxy.send(flag, EVENT_NAME, rtn_data, WS_TAG.CONTROL)
            return None

        rtn_data = {
            "status": "success",
            "event" : "process.get_instance_status",
            "inst_id" : inst_id,
            "val": None
        }

        if _get_owner_uid(inst_id) == int(uid):
            _model = {
                "inst_id": inst_id,
                "current_player": -1,
                "total_player": None,
                "RAM": -1,
                "total_RAM": None,
                "status": SERVER_STATE.HALT
            }
            rtn_data["val"] = _model

            _q = db.session.query(ServerInstance).filter(ServerInstance.inst_id == inst_id).first()

            if _q != None:
                _model["total_player"] = _q.max_user
                _model["total_RAM"] = _q.max_RAM
                '''
                if self.watcher.just_get(inst_id) != None:
                    _i_obj = self.watcher.just_get(inst_id)

                    if _i_obj.get("inst") != None:
                        _model["status"] = _i_obj.get("inst").get_status()

                    _model["current_player"] = _i_obj.get("current_player")
                    _model["RAM"] = _i_obj.get("RAM")
                '''
                self.proxy.send(flag, EVENT_NAME, rtn_data, WS_TAG.CONTROL)
            else:
                rtn_data["status"] = "error"
                self.proxy.send(flag, EVENT_NAME, rtn_data, WS_TAG.CONTROL)

        else:
            rtn_data["status"] = "error"
            self.proxy.send(flag, EVENT_NAME, rtn_data, WS_TAG.CONTROL)
        # if the message is sent from browser
        #if sender == WS_TAG.CLIENT:
        #    self.proxy.send(EVENT_NAME, sender,flag, rtn_data, uid=uid)

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
        rtn_data = {
            "status": "success",
            "inst_id": None
        }

        inst_id = values.get("inst_id")

        self.watcher.start_instance(inst_id)
        rtn_data["inst_id"] = inst_id


    def stop_instance(self, flag, values):
        '''
        DESCRIPTION: stop a instance.

        EVENT_NAME: process.stop_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        EVENT_NAME = "process.stop_instance"
        uid, sid, src, dest = self.pool.get(flag)

        inst_id = values.get("inst_id")

        if inst_id == None:
            return None
        rtn_data = {
            "status": "success",
            "event" : EVENT_NAME,
            "inst_id": inst_id
        }

        if self.watcher.just_get(inst_id) == None:
            rtn_data["status"] = "error"
            self.proxy.send(flag, "process.response", rtn_data, WS_TAG.CONTROL)

        self.watcher.stop_instance(inst_id)
        rtn_data["inst_id"] = inst_id

    def _test(self, flag, values):
        print("[MPW] Roger. flag =%s, values= %s, info = %s" % (flag, values, self.pool.get(flag)))

    def add_and_start(self, flag, values):
        self.start_instance(flag, values,send_ack=False)

    def restart_instance(self, flag, values):
        self.stop_instance(flag, values)
        self._restart_flag.set(int(values.get("inst_id")), True)

    def send_command(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)
        inst_id = values.get("inst_id")
        command = values.get("command")
        if inst_id == None:
            return None
        self.watcher.send_command(inst_id, command)

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

        # KEY : <inst_id>
        # VALUE : <uid>
        self._inst_uid_cache = {}

        _names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout",
                  "inst_player_change","inst_memory_change")

        gc = GlobalConfig.getInstance()

        # add hook function
        for item in _names:
            _method = getattr(self, "on_%s" % item)
            self.add_hook_func(item, _method)

        # add inst_id -> uid cache from database
        if gc.get("init_super_admin") == True:
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
        proxy = MessageQueueProxy(WS_TAG.MPW)
        event_prefix = "process"
        event_type   = "broadcast"

        _name   = "%s.%s" % (event_prefix, event_type)
        values = {
            "inst_id" : inst_id,
            "event" : event_name,
            "val" : value
        }
        uid = self._get_uid_from_inst_id(inst_id)
        proxy.send(None, _name, values, WS_TAG.CONTROL, uid = uid)

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
