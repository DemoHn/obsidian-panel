from app import db
from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy
from app.model import ServerInstance, JavaBinary, ServerCORE

import os
import math

class ProcessEventHandler(MessageEventHandler):
    __prefix__ = "process"

    def __init__(self):
        # denote message proxy for sending message
        # Don't worry, it's a singleton class
        self.proxy = MessageQueueProxy(WS_TAG.CONTROL)
        MessageEventHandler.__init__(self)

    def _test(self, flag, values):
        # just for testing
        self.proxy.send(flag, "process._test", values, WS_TAG.MPW)

    def start(self, flag, values):
        # _inst_running_sig = signals.signal("inst")
        # hook functions
        inst_id = values.get("inst_id")
        uid = values.get("_uid")

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

            watcher_event = "process.add_and_start"

            inst_values = {
                "inst_id": inst_id,
                "port": _port,
                "config": mc_w_config,
            }
            self.proxy.send(flag, watcher_event, inst_values, WS_TAG.MPW)

    def stop(self, flag, values):
        pass

    def broadcast(self, flag, values):
        # broadcast data to multiple clients
        pass
