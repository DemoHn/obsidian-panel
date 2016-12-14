__author__ = "Nigshoxiz"

import sqlite3
import os
import traceback
import logging
from ob_logger import Logger
logger = Logger("GbConf", debug=True)

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class GlobalConfigDatabase(object):
    """
    This database manages ob_panel global configuration.
    For simplicity, we use Python's sqlite3 module directly (instead of sql_alchemy)
    to execute SQL operations.
    """
    def __init__(self):
        self.BASE_DIR = os.path.join(os.path.expanduser("~"),"ob_panel")
        self.SQLITE_DIR = os.path.join(self.BASE_DIR, "sql")

        SQLITE_DIR = self.SQLITE_DIR

        if not os.path.isdir(SQLITE_DIR):
            os.makedirs(SQLITE_DIR)
        config_db_file = os.path.join(SQLITE_DIR, "_global_config.db")

        # NOTE : set isolation_level to None to close autocommit mode
        self.conn = sqlite3.connect(config_db_file, isolation_level=None, check_same_thread=False)
        self.db_name = "_global_config"
        self.logger = logger
        self.init_table()

    def init_table(self):
        c = self.conn.cursor()
        table_str = "CREATE TABLE IF NOT EXISTS config (conf_key TEXT, conf_value TEXT)"
        c.execute(table_str)
        self.conn.commit()

    def init_data(self,default_values):
        c = self.conn.cursor()
        try:
            #c.execute("begin")
            for key in default_values:
                _key = key
                _val = str(default_values.get(key))

                if self.read(_key) == None:
                    insert_str = "INSERT OR REPLACE into config (conf_key, conf_value) VALUES (?,?)"
                    c.execute(insert_str,(_key,_val))
                    self.conn.commit()
            #c.execute("commit")
        except self.conn.Error:
            self.logger.error(traceback.format_exc())
            c.execute("rollback")

        #self.conn.close()

    def delete(self, key):
        _list_flag = False
        c = self.conn.cursor()

        if type(key) == list:
            _list_flag = True
        try:
            del_str = "DELETE FROM config WHERE conf_key = ?"
            if _list_flag:
                c.execute("begin")
                for item in key:

                    c.execute(del_str,[item])
                c.execute("commit")
            else:
                c.execute(del_str,[key])
                self.conn.commit()

        except self.conn.Error:
            self.logger.error(traceback.format_exc())
            if _list_flag:
                c.execute("rollback")

    def add(self, key, new_value):
        c = self.conn.cursor()
        try:
            sel_str = "insert or replace into config (conf_key, conf_value) VALUES (?,?)"
            c.execute(sel_str, [key, new_value])
            self.conn.commit()
        except self.conn.Error:
            self.logger.error(traceback.format_exc())

    def update(self, key, new_value):
        c = self.conn.cursor()
        try:
            sel_str = "update config set conf_value = ? where conf_key = ?"
            c.execute(sel_str, [new_value, key])
            self.conn.commit()
        except self.conn.Error:
            self.logger.error(traceback.format_exc())

    def read(self, key):
        c = self.conn.cursor()
        try:
            sel_str = "select * from config where conf_key = ?"
            c.execute(sel_str,[key])
            data = c.fetchone()
            if data == None:
                return None
            return data[1]
        except self.conn.Error:
            self.logger.error(traceback.format_exc())

    def read_all(self):
        rtn = {}
        c = self.conn.cursor()
        try:
            sel_str = "SELECT * FROM config"
            c.execute(sel_str)
            data = c.fetchall()
            for row in data:
                rtn[row[0]] = row[1]
            return rtn
        except self.conn.Error:
            self.logger.error(traceback.format_exc())

class GlobalConfig(metaclass=Singleton):
    """
    GlobalConfig class
    """
    instance = None

    def __init__(self):
        """
        Frankly, 'gdb' means 'Global config DataBase',
        not the well-known GNU/Linux debugger!!
        """
        self.gdb = GlobalConfigDatabase()
        self.logger = logger

        base_dir = self.gdb.BASE_DIR

        self.default_values = {
            "init_super_admin" : "False",
            "base_dir": base_dir,
            "uploads_dir" : os.path.join(base_dir,"uploads"),
            "files_dir" : os.path.join(base_dir,"files"),
            "servers_dir" : os.path.join(base_dir,"servers"),
            "lib_bin_dir" : os.path.join(base_dir,"env"),
            "sqlite_dir" : self.gdb.SQLITE_DIR,

            # temporal super admin database
            "temp_superadmin_username":"",
            "temp_superadmin_email":"",
            "temp_superadmin_hash":"",

            "database_uri" : "",

            "_RESTART_LOCK" : "False",

            "_temp_java_binary" : "", # records java binary you installed
            "_temp_server_core" : "", # records of server core
        }

        self.gdb.init_data(self.default_values)

    @staticmethod
    def getInstance():
        if GlobalConfig.instance == None:
            GlobalConfig.instance = GlobalConfig()
        return GlobalConfig.instance

    def get(self, property):
        data = self.gdb.read(property)

        # string to bool
        if data == "False" or data == "false":
            return False
        elif data == "True" or data == "true":
            return True
        else:
            return data

    def set(self, property, name):
        self.gdb.update(property, name)

    def delete(self, key):
        self.gdb.delete(key)
    # ob_init_flag
    def enableInitFlag(self):
        self.gdb.update("ob_init_flag","True")

    def disableInitFlag(self):
        self.gdb.update("ob_init_flag","False")

    def getInitFlag(self):
        self.get("ob_init_flag")
