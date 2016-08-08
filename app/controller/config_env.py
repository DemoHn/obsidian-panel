__author__ = "Nigshoxiz"

from app.controller.global_config import GlobalConfig

import tarfile
import os,re
import shutil
import subprocess
import pymysql
import logging
import traceback
import threading

class DatabaseEnv(GlobalConfig):
    """
    class DatabaseEnvironment:
    """
    def __init__(self):
        GlobalConfig.__init__(self)
        self.__keys = (
            "db_type",
            "db_name",
            "db_mysql_ip",
            "db_mysql_username",
            "db_mysql_password"
        )

        if self.get("init_super_admin") == False:
            self.gdb.init_data({
                "db_type" : "sqlite",
                "db_name" : "ob_panel",
                "db_mysql_ip" : "127.0.0.1",
                "db_mysql_username" : "root",
                "db_mysql_password" : ""
            })

        self._logger = logging.getLogger("ob_panel")

    def setDatabaseType(self, db_type):
        types = ("sqlite", "mysql")
        if db_type in types:
            self.set("db_type", db_type)
            return True
        else:
            return False

    def getDatabaseType(self):
        return self.get("db_type")

    def setMySQLinfo(self, MySQL_username, MySQL_password):
        self.set("db_mysql_username", MySQL_username)
        self.set("db_mysql_password", MySQL_password)

    def testMySQLdb(self, MySQL_username, MySQL_password):
        try:
            _ip = self.get("db_mysql_ip")
            conn = pymysql.connect(host=_ip, user=MySQL_username, passwd=MySQL_password)
        except ConnectionRefusedError:
            self._logger.warning("Database refused connection. Maybe your MySQL server haven't run yet?")
            self._logger.warning(traceback.format_exc())
            return False
        except pymysql.err.Error:
            self._logger.warning("MySQL login error. See the following log for details.")
            self._logger.warning(traceback.format_exc())
            return False
        except:
            self._logger.warning(traceback.format_exc())
            return False

        return True

class JavaEnv(GlobalConfig):
    def __init__(self):
        GlobalConfig.__init__(self)
        self.__keys = (
            "sys_java_dir",
            "sys_java_version",
            "default_java_dir"
        )

    def findSystemJavaInfo(self):
        """
        find the execution directory of the pre-installed java Runtime (if so).
        :return: (<java_dir>, <java_version>)
        """
        java_dir = shutil.which('java')

        if java_dir == None:
            return (None, None)
        else:
            self.set("sys_java_dir", java_dir)
            p = subprocess.Popen(java_dir+" -version", shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT
                                 )

            _pb = p.communicate()
            version_string_arr = _pb[0].decode("utf-8").split("\n")
            g = re.search("[0-9\.\_]+", version_string_arr[0])
            version = g.group()
            self.set("sys_java_version", version)
            return (java_dir, version)

    def findUserJavaInfo(self):
        bin_dir = self.get("lib_bin_dir")
        dirs = []
        user_java_infos = []
        # add subdirs in this directory
        for item in os.listdir(bin_dir):
            _dir = os.path.join(bin_dir, item)
            if os.path.isdir(_dir):
                # java executable exists
                if os.path.isfile(os.path.join(_dir,"bin/java")):
                    dirs.append(_dir)

        # next, check java version
        for item in dirs:
            java_executable = os.path.join(item, "bin/java")
            p = subprocess.Popen(java_executable+" -version", shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

            _pb = p.communicate()

            version_string_arr = _pb[0].decode("utf-8").split("\n")
            g = re.search("[0-9\.\_]+", version_string_arr[0])

            if g != None:
                version = g.group()
                _model = {
                    "dir" : java_executable, # parent directory
                    "version" : version
                }
                user_java_infos.append(_model)

        return user_java_infos
