import os
import traceback
import random

from app.tools.mc_wrapper import MCProcessPool
from app.tools.mc_wrapper.instance import MCServerInstanceThread
from app.controller.global_config import GlobalConfig
# models
from app.model.ob_server_instance import ServerInstance
from app.model.ob_java_bin import JavaBinary
from app.model.ob_server_core import ServerCORE
from app.model.ob_user import Users

from app.blueprints.server_inst import logger
from app import db

class UserInstance(MCProcessPool):
    def __init__(self, uid):
        self._port_range = [20000, 30000]
        self._cwd_dir = ""
        self._java_dir = ""

        self.inst_name = ""
        self.inst_port = 0
        self.inst_config = {}
        self.inst_properties = {}

        self.owner_id = uid
        self.inst_RAM = None
        self.java_bin_id = None
        self.server_core_id = None

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
        # get registered ports of all instances
        ports = []
        _all = db.session.query(ServerInstance).all()

        for _item in _all:
            ports.append(_item["listening_port"])

        _index = 0
        while True:
            _index += 1
            num = random.randint(self._port_range[0], self._port_range[1])

            if num not in ports:
                return num

            # prevent for infinite loop
            if _index > 2000:
                return None
        pass

    def _set_inst_directory(self):
        '''
        In order to create a new instance, we have to create an individual space to
        store files first.
        :return:
        '''
        gc = GlobalConfig.getInstance()
        servers_dir = gc.get("servers_dir")

        owner = db.session.query(ServerInstance).join(Users).filter(Users.id == self.owner_id).first()
        owner_name = owner.username
        curr_id = ServerInstance.query(ServerInstance.inst_id).count()
        dir_name =  "%s_%s" % (owner_name, (curr_id+1))

        logger.debug("[user_inst] dir_name = %s" % dir_name)
        return os.path.join(servers_dir, dir_name)
        pass

    def set_instance_name(self, name):
        '''
        :param name: the instance's name. It will be shown on the instance list.
        encoded in utf-8.
        :return:
        '''
        if name == "" or name == None:
            try:
                # get current id of instance
                curr_id = ServerInstance.query(ServerInstance.inst_id).count()
                logger.debug("curr_id  = %s" % curr_id)

                new_name = "Inst - %s" % (curr_id + 1)
                self.inst_name = new_name
                return new_name
            except:
                logger.error(traceback.format_exc())
                return None
        else:
            self.inst_name = name
            return name

    def set_instance_properties(self, properties):
        self.inst_properties = properties
        pass

    def set_allocate_RAM(self, RAM):
        '''
        max allocatable RAM
        :param RAM:
        :return:
        '''
        # TODO add logic of different type of users
        _RAM = int(RAM)

        self.inst_config["max_RAM"] = _RAM
        self.inst_config["min_RAM"] = _RAM / 2

        self.inst_RAM = _RAM
        return _RAM
        pass

    def set_java_bin(self, java_bin_id):
        # check if java_bin_id exists
        res = db.session.query(JavaBinary).filter(JavaBinary.id == java_bin_id).first()

        if res == None:
            return None
        else:
            self.java_bin_id = java_bin_id
            return java_bin_id

    def set_server_core(self, core_file_id):
        # check if core_file_id exists
        res = db.session.query(ServerCORE).filter(ServerCORE.core_id == core_file_id).first()

        if res == None:
            return None
        else:
            self.server_core_id = core_file_id
            return core_file_id

    def create_inst(self):
        '''
        Check config information, and insert data into db.
        REMINDER: This operation will NEVER run the server!
        :return: instance id
        '''
        # check if server_core_file and java runtime binary has been set
        # correctly.
        if self.server_core_id == None or \
                        self.java_bin_id == None or self.inst_RAM == None:
            return None

        # then create dir
        _work_dir = self._set_inst_directory()
        self.inst_config["proc_cwd"] = _work_dir
        os.makedirs(_work_dir)

        # and


        pass

    def remove_inst(self, inst_id):
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
