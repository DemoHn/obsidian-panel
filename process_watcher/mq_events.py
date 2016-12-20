from app import db
from app.model import ServerInstance
from app.controller.global_config import GlobalConfig
from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy, Singleton

from . import SERVER_STATE, logger
from .watcher import Watcher
from .process_pool import MCProcessPool

class WatcherEvents(MessageEventHandler):
    '''
    This class handles control events from other side (app,websocket and so on).
    Of course, since the watcher is an independent process, we use message queue
    to control it.
    '''
    __prefix__ = "process"
    def __init__(self):
        self.watcher = Watcher()
        self.proc_pool = MCProcessPool()
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
        uid, sid, src, dest = self.pool.get(flag)
        EVENT_NAME = "process.response"

        inst_id = int(values.get("inst_id"))

        if inst_id == None:
            rtn_data = {
                "status" : "error",
                "inst_id" : inst_id,
                "val" : None
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

        inst_info = self.proc_pool.get_info(inst_id)
        if inst_info.get_owner() == int(uid):
            _curr_player = -1
            _RAM = -1
            if inst_info.get_current_player() != None:
                _curr_player = inst_info.get_current_player()

            if inst_info.get_RAM() != None:
                _RAM = inst_info.get_RAM()

            _model = {
                "inst_id": inst_id,
                "current_player": _curr_player,
                "total_player": inst_info.get_total_player(),
                "RAM": _RAM,
                "total_RAM": inst_info.get_total_RAM(),
                "status": self.proc_pool.get_status(inst_id)
            }
            rtn_data["val"] = _model

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
        return None
        #========= TODO TODO TODO ==============
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

    def start_instance(self, flag, values):
        '''
        DESCRIPTION: start a instance.

        EVENT_NAME: process.start_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        inst_id = int(values.get("inst_id"))
        uid, sid, src, dest = self.pool.get(flag)

        inst_info = self.proc_pool.get_info(inst_id)

        if inst_info.get_owner() == int(uid):
            self.watcher.start_instance(inst_id)

    def stop_instance(self, flag, values):
        '''
        DESCRIPTION: stop a instance.

        EVENT_NAME: process.stop_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        uid, sid, src, dest = self.pool.get(flag)
        inst_id = values.get("inst_id")

        if inst_id == None:
            return None

        inst_info = self.proc_pool.get_info(inst_id)
        inst_daemon = self.proc_pool.get_daemon(inst_id)

        if inst_info == None:
            return None

        if inst_info.get_owner() == uid:
            # normal exit, do not restart the instance anymore
            inst_daemon.set_normal_exit(True)
            self.watcher.stop_instance(inst_id)

    def add_and_start(self, flag, values):
        self.start_instance(flag, values)

    def restart_instance(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)
        inst_id = values.get("inst_id")

        inst_info = self.proc_pool.get_info(inst_id)
        inst_daemon = self.proc_pool.get_daemon(inst_id)

        if inst_info == None:
            return None

        if inst_info.get_owner() == uid:
            inst_daemon.set_normal_exit(True)
            # restart flag
            inst_daemon.set_restart_flag(True)
            self.watcher.stop_instance(inst_id)

    def send_command(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)
        inst_id = values.get("inst_id")
        command = values.get("command")
        if inst_id == None:
            return None

        inst_info = self.proc_pool.get_info(inst_id)
        if inst_info.get_owner() == uid:
            self.watcher.send_command(inst_id, command)
