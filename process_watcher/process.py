from . import SERVER_STATE, logger
from .parser import ServerPropertiesParser
from .process_callback import MCProcessCallback

import traceback, os
import pyuv

class MCProcess(MCProcessCallback):
    def __init__(self, inst_id, loop=None, mc_w_config=None):
        MCProcessCallback.__init__(self)
        self._pid = None
        self._proc_config =  mc_w_config
        # event loop
        if loop == None:
            self._loop = pyuv.Loop()
        else:
            self._loop = loop
        # pipes
        self._stdin_pipe = pyuv.Pipe(self._loop, True)
        self._stdout_pipe = pyuv.Pipe(self._loop, True)
        # inst_id
        # You know, one MC instance only ownes one process class
    def _init_env(self, proc_cwd, port):
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
        parser.set_server_port(port)
        # write config to the file
        parser.dumps()

    # process events
    def on_read(self, pipe_handle, data, error):
        logger.debug(data)
        pass

    # TODO
    def on_terminate(self, timer_handle):
        self._pid = None

    def on_exit(self, status, signal):
        self._pid = None

    def load_config(self, mc_w_config):
        self._proc_config = mc_w_config

    def start_process(self):
        # check config
        if self._proc_config == None:
            raise TypeError

        mc_w_config = self._proc_config
        # set args
        cmd_args = [mc_w_config.java_bin,
                    "-Xms%sM" % int(mc_w_config.min_RAM),
                    "-Xmx%sM" % int(mc_w_config.max_RAM),
                    "-jar",
                    mc_w_config.jar_file,
                    "nogui"]

        self._init_env(mc_w_config.proc_cwd, mc_w_config.port)
        logger.debug("cmd args: %s" % cmd_args)
        # set pipes
        stdin  = pyuv.StdIO(stream=self._stdin_pipe, flags=pyuv.UV_CREATE_PIPE | pyuv.UV_READABLE_PIPE)
        stdout = pyuv.StdIO(stream=self._stdout_pipe, flags=pyuv.UV_CREATE_PIPE | pyuv.UV_READABLE_PIPE)
        stderr = pyuv.StdIO(stream=self._stdout_pipe)

        # spawn process
        proc = pyuv.Process.spawn(self._loop,
                                  args=cmd_args,
                                  exit_callback=self.on_exit,
                                  stdio=[stdin, stdout, stderr],
                                  cwd=mc_w_config.proc_cwd,
                                  flags=pyuv.UV_PROCESS_DETACHED)
        # set pid
        self._pid = proc.pid
        logger.info("Start Process pid=(%s)" % self._pid)

        # on read
        self._stdout_pipe.start_read(self.on_read)
        return True

    def stop_process(self):
        if self._pid != None:
            logger.info("kill process pid=(%s)" % self._pid)
            self.send_command("stop")
        else:
            logger.error("kill process Failed!")

    # this only happens when no response even prompting `stop` command
    # TODO
    def terminate_process(self):
        pass

    def send_command(self, command):
        _command = (command + "\n").encode()
        logger.debug("write command: %s" % command)
        if not self._stdin_pipe.closed:
            self._stdin_pipe.write(_command)

    def get_pid(self):
        return self._pid
