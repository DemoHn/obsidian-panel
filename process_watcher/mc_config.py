__author__ = "Nigshoxiz"
import os
class MCWrapperConfig():

    __counter = 0
    """MC Wrapper Configurations.
    Note: These configuration items are mainly used for starting server process.
    """
    @property
    def java_bin(self):
        return self._java_bin

    @java_bin.setter
    def java_bin(self,value):
        if value == None:
            self._java_bin = "/usr/bin/java"
        else:
            self._java_bin = os.path.normpath(value)

    @property
    def min_RAM(self):
        return self._min_RAM

    @min_RAM.setter
    def min_RAM(self, RAM):
        if RAM == None:
            self._min_RAM = 1
        else:
            self._min_RAM = int(RAM)

    @property
    def max_RAM(self):
        return self._max_RAM

    @max_RAM.setter
    def max_RAM(self, RAM):
        if RAM == None:
            self._max_RAM = 1
        else:
            self._max_RAM = int(RAM)

    @property
    def jar_file(self):
        return self._jar_file

    @jar_file.setter
    def jar_file(self,file):
        if file == None:
            raise FileNotFoundError
        else:
            self._jar_file = os.path.normpath(file)

    @property
    def proc_cwd(self):
        return self._proc_cwd

    @proc_cwd.setter
    def proc_cwd(self,dir):
        _tmp_dir = os.path.expanduser("~")
        if dir == None:
            _tmp_dir = os.path.join(_tmp_dir, str(MCWrapperConfig.__counter))
        else:
            _tmp_dir = os.path.normpath(dir)

        if not os.path.isdir(_tmp_dir):
            os.makedirs(_tmp_dir)

        self._proc_cwd = _tmp_dir

    def __init__(self,**kwargs):
        """Config entries:
                java_bin : java executable location. (On Linux with java installed, it's /usr/bin/java)
                min_RAM   : minimum RAM allocated for this process. (unit : MB)
                max_RAM   : maximum RAM allocated for this process. (unit: MB)
                jar_file : MC server jar file's location. (generally, the name is `minecraft_server_**.jar`)
                proc_cwd : literally, it means MC server's working directory. But here, it determines where to save
                  the world's data.

        """
        MCWrapperConfig.__counter += 1

        self._java_bin = None
        self._min_RAM  = None
        self._max_RAM  = None
        self._jar_file = None
        self._proc_cwd = None

        self.java_bin = kwargs.get("java_bin")
        self.min_RAM  = kwargs.get("min_RAM")
        self.max_RAM  = kwargs.get("max_RAM")
        self.jar_file = kwargs.get("jar_file")
        self.proc_cwd = kwargs.get("proc_cwd")
        pass
