import logging
import os

class MCProcessPool():
    """
    Minecraft Server Instance Pool.
    This pool stores all MCServerInstance(), which directly
    start, stop and monitor MC server process.
    """
    instance = None
    def __init__(self):
        # Process Pool
        # format:
        # {
        #    [port]: MCServerInstance()
        # }
        self.processPool = {}

    @staticmethod
    def getInstance():
        """
        One MC wrapper should only own one MCProcessPool().
        call `MCProcessPool.getInstance()` to ensure there's only one instance of this class.
        :return: [class instance]
        """
        if MCProcessPool.instance == None:
            MCProcessPool.instance = MCProcessPool()
        return MCProcessPool.instance

    def count(self):
        return len(self.processPool)

    # if server instance exists or this port
    def exists(self,port):
        if self.processPool.get(str(port)) is None:
            return False
        else:
            return True

    def add(self, port, proc_instance):
        port = str(port)
        # add dict
        self.processPool[port] = proc_instance

    def remove(self , port):
        port = str(port)
        if self.processPool.get(port) != None:
            del self.processPool[port]

    def get(self , port):
        port = str(port)
        return self.processPool[port]

    def add_lock(self, port):
        """
        Add a simple lock
        :param port: listening port
        :return:
        """
        _str = "__%s_lock" % port
        self.processPool[_str] = True

    def lock_exists(self, port):
        _str = "__%s_lock" % port
        return self.processPool.get(_str) != None

    def del_lock(self, port):
        _str = "__%s_lock" % port
        if self.processPool.get(_str) != None:
            del self.processPool[_str]

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
            self._min_RAM = float(RAM)

    @property
    def max_RAM(self):
        return self._max_RAM

    @max_RAM.setter
    def max_RAM(self, RAM):
        if RAM == None:
            self._max_RAM = 1
        else:
            self._max_RAM = float(RAM)

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
                min_RAM   : minimum RAM allocated for this process. (unit : GB)
                max_RAM   : maximum RAM allocated for this process.
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


# logging
def init_logging_system(debug=True):
    logger = logging.getLogger(__name__)

    if debug == True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # add handler , just shows log via stderr
    s_handler = logging.StreamHandler()
    s_formatter = logging.Formatter('%(asctime)-15s [%(levelname)s] %(message)s',
                                    datefmt="%Y-%m-%d %H:%M:%S")

    s_handler.setFormatter(s_formatter)
    logger.addHandler(s_handler)

    return logger

# set logger
'''
if __name__ == "__main__":
    _logger = init_logging_system()
else:
    _logger = logging.getLogger(__name__)
'''
_logger = init_logging_system()
logger = _logger
mc_pool = MCProcessPool.getInstance()