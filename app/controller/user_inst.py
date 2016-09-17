import os
import traceback
import random
import shutil
import math
import time

#from app.tools.mc_wrapper import MCProcessPool
#from app.tools.mc_wrapper.instance import MCServerInstanceThread
from mpw.parser import ServerPropertiesParser
from app.controller.global_config import GlobalConfig
# models
from app.model import ServerInstance, JavaBinary, ServerCORE, Users
from app import socketio
from app.blueprints.server_inst import logger
from app import db, watcher

class UserInstance():
    def __init__(self, uid):
        self._port_range = [20000, 30000]
        self._cwd_dir = ""
        self._java_dir = ""

        self.inst_name = None
        self.inst_port = 0
        self.inst_properties = {}
        self.max_user = 0
        self.owner_id = uid
        self.inst_RAM = None
        self.java_bin_id = None
        self.server_core_id = None

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
            ports.append(_item.listening_port)

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

        owner = db.session.query(Users).filter(Users.id == self.owner_id).first()

        owner_name = owner.username
        curr_id = db.session.query(db.func.max(ServerInstance.inst_id)).scalar()

        if curr_id == None:
            curr_id = 0

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
                curr_id = db.session.query(db.func.max(ServerInstance.inst_id)).scalar()
                if curr_id == None:
                    curr_id = 0

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

    def set_listening_port(self, port=None):
        if port == None:
            _port = self._auto_assign_port()
            self.inst_port = _port
            self.inst_properties["server-port"] = _port
            return _port
        else:
            self.inst_port = int(port)
            self.inst_properties["server-port"] = int(port)
            return int(port)

    def set_instance_properties(self, properties):
        for keys in properties:
            self.inst_properties[keys] = properties.get(keys)
        pass

    def set_max_user(self, user_num):
        _user_num = int(user_num)
        self.max_user = _user_num
        self.inst_properties["max-players"] = _user_num
        return _user_num

    def set_allocate_RAM(self, RAM):
        '''
        max allocatable RAM
        :param RAM:
        :return:
        '''
        # TODO add logic of different type of users
        _RAM = int(RAM)
        self.inst_RAM = _RAM
        return _RAM
        pass

    def set_java_bin(self, java_bin_id):
        # check if java_bin_id exists
        res = db.session.query(JavaBinary).filter(JavaBinary.id == java_bin_id).first()

        if res == None:
            raise Exception("java_bin_id '%s' not found in database!" % java_bin_id)
        else:
            self.java_bin_id = java_bin_id
            return java_bin_id

    def set_server_core(self, core_file_id):
        # check if core_file_id exists
        res = db.session.query(ServerCORE).filter(ServerCORE.core_id == core_file_id).first()

        if res == None:
            raise Exception("server_core '%s' not found in database!" % core_file_id)
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

        _null_value_asserts_ = (
            ("server_core_id", None),
            ("java_bin_id", None),
            ("inst_RAM", None),
            ("inst_name", None),
            ("max_user", 0),
            ("inst_port", 0)
        )
        # value asserts
        for _asserts in _null_value_asserts_:
            if hasattr(self, _asserts[0]):
                val = getattr(self, _asserts[0])

                if val == _asserts[1]:
                    raise Exception("property '%s' is '%s', value asserts failed!" % (_asserts))

        # then create directory
        _work_dir = self._set_inst_directory()
        # mkdir -p
        if not os.path.exists(_work_dir):
            os.makedirs(_work_dir)

        s_p_file = os.path.join(_work_dir, "server.properties")
        # touch server.properties file if not exists
        _f = open(s_p_file,"a")
        _f.close()
        # then generate server.properties file

        parser = ServerPropertiesParser(s_p_file)
        parser.write_config(self.inst_properties)

        try:
            # add data to database
            inst_data = ServerInstance(
                owner_id = self.owner_id,
                inst_name = self.inst_name,
                core_file_id = self.server_core_id,
                java_bin_id = self.java_bin_id,
                listening_port = self.inst_port,
                max_RAM = self.inst_RAM,
                max_user = self.max_user,
                inst_dir = _work_dir
            )

            db.session.add(inst_data)
            db.session.commit()
        except:
            logger.error(traceback.format_exc())
            return None

        # query database
        inst_id = db.session.query(db.func.max(ServerInstance.inst_id)).scalar()
        return inst_id

    def remove_inst(self, inst_id):
        # read work dir
        _inst_id = inst_id
        res = ServerInstance.query.filter(inst_id == _inst_id).first()

        if res == None:
            return None
        else:
            work_dir = res.inst_dir
            # remove all files of the working dir
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
            # remove item from database

            db.session.query(ServerInstance).filter(ServerInstance.inst_id == _inst_id).delete()
            db.session.commit()

class InstanceController(object):
    '''
    main controller of all MC server instances.
    REMINDER: all methods are static methods, thus you have to
    offer the instance id first.
    '''

    @staticmethod
    def start(inst_id):
        # _inst_running_sig = signals.signal("inst")
        # hook functions
        def _send_log_func(log_data):
            logger.debug("inst[%s] log %s" % (inst_id, log_data))
            #_send_log_sig.send((inst_id, log_data))

            socketio.emit("recv",log_data)
        def _inst_starting_func():
            logger.debug("inst[%s] START" % inst_id)
            #_inst_starting_sig.send(inst_id)

        _q = db.session.query(ServerInstance).join(JavaBinary).join(ServerCORE)
        item = _q.filter(ServerInstance.inst_id == inst_id).first()

        if item == None:
            raise Exception("Item is None!")
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
            watcher.add_instance(inst_id, _port, mc_w_config)

            watcher.start_instance(inst_id)
            #_running_inst = watcher.get_instance(inst_id)
            #_running_inst.add_hook("data_received", _send_log_func)
            #_running_inst.add_hook("inst_starting", _inst_starting_func)
        #mc_pool = MCProcessPool.getInstance()
        # retrieve instance info from database

        #t = MCServerInstanceThread(port= _port, config = mc_w_config)

        #mc_pool.add(_port, t)
        #t.start()

        # add hooks

    @staticmethod
    def stop(inst_id):
        #mc_pool = MCProcessPool.getInstance()

        _q = db.session.query(ServerInstance)
        _inst = _q.filter(ServerInstance.inst_id == inst_id).first()

        if _inst == None:
            raise Exception('instance info is NULL!')
        else:
            #s = mc_pool.get(_port).inst._status
            s = watcher.get_instance(inst_id)
            if s != None:
                _status = s._status
                print("current status: %s" % _status)
            #mc_pool.get(_port).inst.stop_process()
            watcher.stop_instance(inst_id)
            # TODO don't forget clear instance dict in <mpw.watcher.proc_pool>

    @staticmethod
    def restart(inst_id):
        InstanceController.stop(inst_id)
        time.sleep(2)
        InstanceController.start(inst_id)