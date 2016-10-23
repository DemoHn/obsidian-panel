__author__ = "Nigshoxiz"

from app import db
from app.utils import WS_TAG
from app.model import ServerInstance, JavaBinary, ServerCORE
from websocket_server.controller.controller import Controller

import os
import math

class ControllerOfInstance(Controller):
    # relax. Just add methods as you want
    prefix = "instance"
    def __init__(self):
        Controller.__init__(self, prefix=ControllerOfInstance.prefix)

    def start(self, flag, values):
        # _inst_running_sig = signals.signal("inst")
        # hook functions
        inst_id = values.get("inst_id")
        uid     = values.get("_uid")

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

            Watcher_Event = "process.add_and_start"

            inst_values = {
                "inst_id" : inst_id,
                "port" : _port,
                "config" : mc_w_config,
                "_uid" : uid
            }

            self.proxy.send(Watcher_Event, WS_TAG.MPW, flag, inst_values)

    def stop(self, inst_id):
        pass

