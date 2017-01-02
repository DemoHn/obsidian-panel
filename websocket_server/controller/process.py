from app import db
from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy
from app.model import ServerInstance, JavaBinary, ServerCORE

from websocket_server.server import WSConnections
import os
import math

class ProcessEventHandler(MessageEventHandler):
    __prefix__ = "process"

    def __init__(self):
        # denote message proxy for sending message
        # Don't worry, it's a singleton class
        #self.proxy = MessageQueueProxy(WS_TAG.CONTROL)
        MessageEventHandler.__init__(self)

    def start(self, flag, values, restart=False):
        # _inst_running_sig = signals.signal("inst")
        # hook functions
        inst_id = values.get("inst_id")

        uid, sid, src, dest = self.pool.get(flag)

        _q = db.session.query(ServerInstance).join(JavaBinary).join(ServerCORE)
        item = _q.filter(ServerInstance.inst_id == inst_id).first()

        if item == None:
            raise Exception("[Instance] item is None!")
        elif int(item.owner_id) != int(uid):
            return None
        else:
            # generate config dict
            mc_w_config = {
                "jar_file": os.path.join(item.ob_server_core.file_dir, item.ob_server_core.file_name),
                "java_bin": item.ob_java_bin.bin_directory,
                "max_RAM": int(item.max_RAM),
                "min_RAM": math.floor(int(item.max_RAM) / 2),
                "proc_cwd": item.inst_dir
            }
            _port = int(item.listening_port)

            if restart:
                watcher_event = "_process.restart_instance"
            else:
                watcher_event = "_process.start_instance"

            inst_values = {
                "inst_id": inst_id,
                "port": _port,
                "config": mc_w_config,
            }
            self.proxy.send(flag, watcher_event, inst_values, WS_TAG.MPW)

    def stop(self, flag, values):
        watcher_event = "_process.stop_instance"
        inst_values = {
            "inst_id" : values.get("inst_id")
        }
        self.proxy.send(flag, watcher_event, inst_values, WS_TAG.MPW)

    def restart(self, flag, values):
        self.start(flag, values, restart=True)

    def send_command(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)

        inst_id = values.get("inst_id")
        command = values.get("command")

        _values = {
            "inst_id" : inst_id,
            "command" : command
        }
        self.proxy.send(flag, "_process.send_command", _values, WS_TAG.MPW)

    def broadcast(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)
        _event = values.get("event")

        _values = {
            "event": _event,
            "inst_id": values.get("inst_id"),
            "value": values.get("val"),
        }

        if _event == None:
            return None
        # broadcast data to multiple clients
        ws = WSConnections.getInstance()
        ws.send_data("message", _values, uid=uid)

    # for sending response from previous request
    # the ONLY difference between `broadcast` and `response` is
    # the former one broadcast data to every client that belongs to the
    # user, but `response` method just send to the data back to
    # the request session id.
    def response(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)
        _event = values.get("event")

        _values = {
            "event": _event,
            "flag" : flag,
            "status" : values.get("status"),
            "inst_id": values.get("inst_id"),
            "val": values.get("val")
        }

        if _event == None:
            return None
        # broadcast data to multiple clients
        ws = WSConnections.getInstance()
        ws.send_data("message", _values, sid=sid)

    def get_instance_status(self, flag, values):
        inst_id = values.get("inst_id")
        _values = {
            "inst_id" : int(inst_id)
        }
        self.proxy.send(flag, "_process.get_instance_status", _values, WS_TAG.MPW)

    def get_instance_log(self, flag, values):
        inst_id = values.get("inst_id")
        _values = {
            "inst_id" : int(inst_id)
        }
        self.proxy.send(flag, "_process.get_instance_log", _values, WS_TAG.MPW)
