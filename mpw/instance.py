from . import SERVER_STATE, logger, event_loop

from .parser import ServerPropertiesParser
import signal

import traceback
import subprocess
import inspect
import os

POLL_NULL = 0x00
POLL_IN = 0x01
POLL_OUT = 0x04
POLL_ERR = 0x08
POLL_HUP = 0x10
POLL_NVAL = 0x20


class MCServerInstance():
    def __init__(self, port, watcher=None):
        if watcher == None:
            from .watchdog import Watchdog
            self.watcher = Watchdog.getWDInstance()
        else:
            self.watcher = watcher

        self.port = port
        # init pid
        self._pid = 0
        self._status = SERVER_STATE.HALT
        self._proc = None

        # running hooks
        # OK, not use it temporary
        # instead, we use Watchdog's global hook - 2016.9.17 - Nigshoxiz
        self._inst_starting_hook = []
        self._inst_running_hook = []
        self._data_received_hook = []
        self._connection_lost_hook = []
        self._inst_stop_hook = []

    def _run_hook(self, hook_name, *args):
        _names = ("inst_starting", "inst_running", "data_received", "connection_lost", "inst_stop")

        if hook_name in _names:
            _method = getattr(self, "_%s_hook" % hook_name)

            for _hook_item in _method:
                if inspect.isfunction(_hook_item):
                    _hook_item(*args)

    def init_env(self,proc_cwd):
        if not os.path.isdir(proc_cwd):
            os.makedirs(proc_cwd)
        # init eula.txt
        EULA_txt_file = os.path.join(proc_cwd, "eula.txt")
        if not os.path.isfile(EULA_txt_file):
            # write eula=true into the eula file , or the server process will refuse to start.
            f = open(EULA_txt_file, "w+")
            f.write("eula=true")
            f.close()

        # init server.properties
        s_p_file = os.path.join(proc_cwd, "server.properties")

        # touch server.properties file
        if not os.path.isfile(s_p_file):
            open(s_p_file,"a").close()

        parser = ServerPropertiesParser(s_p_file)
        parser.set_server_port(self.port)
        # write config to the file
        parser.dumps()

    def add_hook(self, hook_name, fn):
        _names = ("inst_starting", "inst_running", "data_received", "connection_lost", "inst_stop")

        if hook_name in _names:
            _method = getattr(self, "_%s_hook" % hook_name)

            if inspect.isfunction(fn):
                _method.append(fn)

    # @params
    # mc_w_config : just an instance of class MCWrapperConfig()
    def start_process(self, mc_w_config):

        #cmd = mc_w_config.java_bin
        cmd_args = [mc_w_config.java_bin,
                    "-Xms%sM" % int(mc_w_config.min_RAM),
                    "-Xmx%sM" % int(mc_w_config.max_RAM),
                    "-jar",
                    mc_w_config.jar_file,
                    "nogui"]

        #logger.info("EXEC CMD: `%s`", " ".join(cmd_args))

        self.init_env(mc_w_config.proc_cwd)
        #transport , process = self.loop.run_until_complete(
            # loop.subprocess_exec(<proc_factory>,cmd, *cmd_args, cwd = mc_w_config.proc_cwd)
            # self.loop.subprocess_exec(asyncio.SubprocessProtocol,cmd, *cmd_args, cwd = mc_w_config.proc_cwd)
        #    self.loop.subprocess_exec(lambda: LogMonitorProtocol(str(self.port)), cmd, *cmd_args, cwd = mc_w_config.proc_cwd)
        #)

        cmd = " ".join(cmd_args)
        self._proc = subprocess.Popen(cmd,shell=True, bufsize=0, cwd=mc_w_config.proc_cwd,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
        # self.loop.add(self._proc.stdout, POLL_IN | POLL_HUP)
        self.watcher.add_f(self._proc.stdout, POLL_IN | POLL_HUP)
        self._pid = self._proc.pid

        logger.debug("PID = %s" % self._pid)
        if self._pid != 0:
            self._status = SERVER_STATE.STARTING
            return self._pid
        else:
            return None
            # self._run_hook("inst_starting")

    def stop_process(self):
        if self._pid > 0:
            logger.info("kill process PID %s" % self._pid)
            self.send_command("stop")
            #os.kill(self._pid, signal.SIGINT)
        else:
            logger.error("Kill Process Falied! PID value is None!")

    # send command
    def send_command(self,command):
        w_pipe = self._proc.stdin
        if w_pipe == None:
            logger.debug("pipe is undefined! Maybe the process is still not created?")
        else:
            _command = (command + "\n").encode("utf-8")
            logger.debug("Write command : "+command)
            if w_pipe.closed == False:
                # Notice: According to the documentation, this method is not recommend,
                # Since it will suck when bufsize > 0.
                # Thus, to use this method, it is vital to set bufsize = 0 on <subprocess.Popen> method
                # Nigshoxiz
                # 2016.9.17
                w_pipe.write(_command)
            else:
                logger.error("pipe No.%s is closed!" % w_pipe.fileno())

    def get_pid(self):
        return self._pid

    def get_status(self):
        return self._status