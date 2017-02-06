from app import db
from app.model import ServerInstance, JavaBinary, ServerCORE
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

    # Any methods begin with '__' will be ignored from registering handlers.
    # So this kind of method is suitable to be used as internal method.
    # Nigshoxiz
    # 21/12/2016
    def __update_pool(self):
        _q = db.session.query(ServerInstance).join(JavaBinary).join(ServerCORE).all()
        # if instances has not been added yet, then it's time to add!
        for item in _q:
            if self.proc_pool.get(item.inst_id) == None:
                self.watcher._add_instance_to_pool(item)

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
        EVENT_NAME = "process.response"

        inst_id = int(values.get("inst_id"))

        if inst_id == None:
            rtn_data = {
                "inst_id" : inst_id,
                "val" : None
            }
            # send error msg
            return rtn_data

        # update pool
        self.__update_pool()

        rtn_data = {
            "inst_id" : inst_id,
            "val": None
        }

        inst_info = self.proc_pool.get_info(inst_id)

        _curr_player = -1
        _RAM = -1
        if inst_info.get_current_player() != None:
            _curr_player = inst_info.get_current_player()

        if inst_info.get_RAM() != None:
            _RAM = inst_info.get_RAM()

        _model = {
            "current_player": _curr_player,
            "total_player": inst_info.get_total_player(),
            "RAM": _RAM,
            "total_RAM": inst_info.get_total_RAM(),
            "status": self.proc_pool.get_status(inst_id)
        }
        rtn_data["val"] = _model

        return rtn_data

    def get_instance_log(self, flag, values):
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
        inst_id = int(values.get("inst_id"))
        if inst_id == None:
            return None

        inst_info = self.proc_pool.get_info(inst_id)

        rtn_data = {
            "inst_id" : inst_id,
            "val": {
                "log" : None
            }
        }

        rtn_data["val"]["log"] = inst_info.get_log()
        return rtn_data

    def add_instance(self, flag, values):
        return None
        '''
        DESCRIPTION: add instance. But not activate it immediately.

        EVENT_NAME: process.add_instance
        :param values: {"inst_id": <inst_id>}
        :return:
        '''
        inst_id = values.get("inst_id")
        uid, sid, src, dest = self.pool.get(flag)

        if inst_id == None:
            return None

        _q = db.session.query(ServerInstance).join(JavaBinary).join(ServerCORE).filter(ServerInstance.inst_id == inst_id).first()
        # inst doesn't exists
        if _q == None:
            return None

        # has added
        if self.proc_pool.get(inst_id) != None:
            return None

        # then add it into proc_pool!
        self.watcher._add_instance_to_pool(_q)

    def remove_instance(self, flag, values):
        # TODO
        return
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
        self.__update_pool()

        inst_info = self.proc_pool.get_info(inst_id)
        self.watcher.start_instance(inst_id)

    def stop_instance(self, flag, values):
        '''
        DESCRIPTION: stop a instance.

        EVENT_NAME: process.stop_instance

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        inst_id = int(values.get("inst_id"))
        if inst_id == None:
            return None

        inst_info = self.proc_pool.get_info(inst_id)
        inst_daemon = self.proc_pool.get_daemon(inst_id)

        if inst_info == None:
            return None

        # normal exit, do not restart the instance anymore
        inst_daemon.set_normal_exit(True)
        self.watcher.stop_instance(inst_id)

    def terminate_instance(self, flag, values):
        '''
        DESCRIPTION: stop an instance brutally.
        This is only used when instance process is experiencing fatal error or lose user's control

        :param values: { "inst_id" : <inst_id> }
        :return:
        '''
        inst_id = int(values.get("inst_id"))
        if inst_id == None:
            return None

        inst_info = self.proc_pool.get_info(inst_id)
        inst_daemon = self.proc_pool.get_daemon(inst_id)

        if inst_info == None:
            return None

        # normal exit, do not restart the instance anymore
        inst_daemon.set_normal_exit(True)
        self.watcher.terminate_instance(inst_id)

    def restart_instance(self, flag, values):
        inst_id = int(values.get("inst_id"))

        inst_info = self.proc_pool.get_info(inst_id)
        inst_daemon = self.proc_pool.get_daemon(inst_id)

        if inst_info == None:
            return None

        inst_daemon.set_normal_exit(True)
        # restart flag
        inst_daemon.set_restart_flag(True)
        self.watcher.stop_instance(inst_id)

    def send_command(self, flag, values):
        inst_id = int(values.get("inst_id"))
        command = values.get("command")
        if inst_id == None:
            return None

        inst_info = self.proc_pool.get_info(inst_id)

        self.watcher.send_command(inst_id, command)
