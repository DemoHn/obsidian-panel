from app.tools.mc_wrapper import MCProcessPool
from app.tools.mc_wrapper.instance import MCServerInstanceThread
from app.controller.global_config import GlobalConfig

from app.model.ob_server_instance import ServerInstance

import os

gc = GlobalConfig.getInstance()

class UserInstance(MCProcessPool):
    def __init__(self):
        self._port_range = [20000, 30000]
        self._cwd_dir = ""
        self._java_dir = ""

        self.inst_name = ""
        self.inst_port = 0
        self.inst_config = {}
        self.inst_RAM = 0

        MCProcessPool.__init__(self)
        self.pool = MCProcessPool.getInstance()
        pass

    def __del__(self):
        pass

    def _auto_assign_port(self):
        '''
        when user doesn't assign the listening port of a server,
        the system will randomly denote it reasonably.

        :return: the assigned port
        '''

        pass

    def _auto_assign_name(self):
        pass

    def _set_inst_directory(self):
        pass

    def set_instance_name(self, name):
        '''
        :param name: the instance's name. It will be shown on the instance list.
        encoded in utf-8.
        :return:
        '''
        if name == "":
            raise NameError
        else:
            self.inst_name = name

    def set_instance_config(self):
        pass

    def set_allocate_RAM(self, RAM):
        pass

    def create_inst(self):
        pass

    def remove_inst(self, inst_id):

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass

def start_mc_server(serv_dir, port):
    mc_w_config = {
        "jar_file":"",
        "max_RAM":"",
        "proc_cwd":""
    }
    pass

def stop_mc_server(port):
    mc_pool = MCProcessPool.getInstance()
    mc_pool.get(port).inst.stop_process()
    pass

def restart_mc_server(port):
    pass
