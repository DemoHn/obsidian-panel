__author__ = "Nigshoxiz"

import sqlite3
from config import SQLITE_DIR
import os
import traceback
import logging

class GlobalConfigDatabase(object):
    """
    This database manages ob_panel global configuration.
    For simplicity, we use Python's sqlite3 module directly (instead of sql_alchemy)
    to execute SQL operations.
    """
    def __init__(self):
        if not os.path.isdir(SQLITE_DIR):
            os.makedirs(SQLITE_DIR)
        config_db_file = os.path.join(SQLITE_DIR, "_global_config.db")

        # NOTE : set isolation_level to None to close autocommit mode
        self.conn = sqlite3.connect(config_db_file, isolation_level=None)
        self.db_name = "_global_config"
        self.logger = logging.getLogger("ob_panel")
        self.init_table()

    def init_table(self):
        c = self.conn.cursor()
        table_str = "CREATE TABLE IF NOT EXISTS config (conf_key TEXT, conf_value TEXT)"
        c.execute(table_str)
        self.conn.commit()

    def init_data(self,default_values):
        c = self.conn.cursor()
        try:
            c.execute("begin")
            for key in default_values:
                _key = key
                _val = str(default_values.get(key))
                insert_str = "INSERT OR REPLACE into config (conf_key, conf_value) VALUES (?,?)"
                c.execute(insert_str,(_key,_val))

            c.execute("commit")
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
        except self.conn.Error:
            self.logger.error(traceback.format_exc())

    def update(self, key, new_value):
        c = self.conn.cursor()
        try:
            sel_str = "update config set conf_value = ? where conf_key = ?"
            c.execute(sel_str, [new_value, key])
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

class GlobalConfig(object):
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
        self.logger = logging.getLogger("ob_panel")

        self.default_values = {
            "init_super_admin" : "False"
        }
        # set 'ob_init_flag=False' and so on
        if self.gdb.read("ob_init_flag") == None:
            self.gdb.init_data(self.default_values)
            self.logger.debug("init GlobalConfig Database")
            self.gdb.add("ob_init_flag","True")

    @staticmethod
    def getInstance():
        if GlobalConfig.instance == None:
            GlobalConfig.instance = GlobalConfig()
        return GlobalConfig.instance

    def get(self, property):
        data = self.gdb.read(property)

        # string to bool
        if data == "False":
            return False
        elif data == "True":
            return True
        else:
            return data

    def set(self, property, name):
        self.gdb.update(property, name)

    # ob_init_flag
    def enableInitFlag(self):
        self.gdb.update("ob_init_flag","True")

    def disableInitFlag(self):
        self.gdb.update("ob_init_flag","False")

    def getInitFlag(self):
        self.get("ob_init_flag")
