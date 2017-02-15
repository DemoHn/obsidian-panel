import os
import traceback
import random
import shutil
import math
import time

from process_watcher.parser import ServerPropertiesParser
from app.controller.global_config import GlobalConfig

# models
from app.model import ServerInstance, JavaBinary, ServerCORE, Users, FTPAccount
from app.blueprints.server_inst import logger
from app import db

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

class EditInstance():
    def __init__(self, inst_id, uid):
        self.uid     = int(uid)
        self.inst_id = int(inst_id)
        self.keys =  (
            "world_name", "number_RAM", "number_players", "listen_port", "core_file_id",
            "java_bin_id", "server_properties", "ftp_account_name", "default_ftp_password"
        )

        self._q_obj = None

    @property
    def q_obj(self):
        if not self._q_obj:
            self._q_obj = db.session.query(ServerInstance).filter(ServerInstance.inst_id == self.inst_id)
        return self._q_obj

    def check_permission(self):
        # check if inst_id is allowed to operate
        _q_obj = db.session.query(ServerInstance).filter(ServerInstance.inst_id == self.inst_id).filter(ServerInstance.owner_id == self.uid)
        if _q_obj.first() == None:
            return False
        else:
            return True

    def check_existance(self):
        _q_obj = db.session.query(ServerInstance).filter(ServerInstance.inst_id == self.inst_id)

        if _q_obj.first() == None:
            return False
        else:
            self._q_obj = _q_obj
            return True

    # return value : (<bool:success>, <code>)
    # e.g.: (True, 200)
    # e.g.: (False, 406)
    def edit_config(self, key, value):
        if not key in self.keys:
            return False
        else:
            method_name = "_set_%s" % key
            method      = getattr(self, method_name)
            try:
                # execute method
                result = method(value)
                return result
            except:
                logger.error(traceback.format_exc())
                return (False, 500)

    # set config
    # notice: prefixed with "_set_"
    def _set_world_name(self, value):
        # check input value
        if value == "" or value == None:
            return (False, 405)
        else:
            world_name_obj = db.session.query(ServerInstance).filter(ServerInstance.inst_name == value).filter(ServerInstance.owner_id == self.uid)
            if world_name_obj.first() != None:
                # duplicated!
                return (False, 406)
            else:
                self.q_obj.update({ "inst_name" : value })
                db.session.commit()
                return (True, 200)

    def _set_number_RAM(self, value):
        if value == "" or type(value) != int:
            return (False, 405)
        else:
            v = int(value) * 1024
            self.q_obj.update({"max_RAM" : v})
            db.session.commit()
            return (True, 200)

    def _set_number_players(self, value):
        if value == "" or type(value) != int:
            return (False, 405)
        else:
            v = int(value)
            self.q_obj.update({"max_user" : v})
            db.session.commit()
            return (True, 200)

    def _set_listen_port(self, value):
        if type(value) != int:
            return (False, 405)
        else:
            v = int(value)
            port_obj = db.session.query(ServerInstance).filter(ServerInstance.listening_port == v)

            if port_obj.first() != None:
                # duplicated!
                return (False, 406)
            else:
                self.q_obj.update({ "listening_port" : v })
                db.session.commit()
                return (True, 200)

    def _set_core_file_id(self, value):
        if type(value) != int:
            return (False, 405)
        else:
            # check existance
            _q = db.session.query(ServerCORE).filter(ServerCORE.core_id == value)
            if _q.first() == None:
                return (False, 404)
            else:
                self.q_obj.update({ "core_file_id" : value })
                db.session.commit()
                return (True, 200)

    def _set_java_bin_id(self, value):
        if type(value) != int:
            return (False, 405)
        else:
            # check existance
            _q = db.session.query(JavaBinary).filter(JavaBinary.id == value)
            if _q.first() == None:
                return (False, 404)
            else:
                self.q_obj.update({ "java_bin_id" : value })
                db.session.commit()
                return (True, 200)

    def _set_server_properties(self, value):
        pass
    def _set_ftp_account_name(self, value):
        pass
    def _set_default_ftp_password(self, value):
        pass
