from . import PipeNo, logger
from .parser import ServerPropertiesParser
from .process_callback import MCProcessCallback

import traceback, os
import pyuv

class MCProcess(MCProcessCallback):
    def __init__(self, inst_id, loop, mc_w_config=None):
        MCProcessCallback.__init__(self)
        self._pid = None
        self._proc_config =  mc_w_config
        # event loop
        self._loop = loop
        self._proc = None
        # pipes
        self._stdin_pipe = None
        self._stdout_pipe = None
        self._stderr_pipe = None
        # inst_id
        # You know, one MC instance only ownes one process class
        self.inst_id = inst_id

        # timer handler
        self._stop_timeout_timer = pyuv.Timer(self._loop)

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
    def on_stdout_read(self, pipe_handle, data, error):
        if error != None:
            logger.error("stdout read error no: %s" % error)
            pipe_handle.close()
        else:
            self.on_log_update(self.inst_id, PipeNo.STDOUT, data.decode())

    def on_stderr_read(self, pipe_handle, data, error):
        if error != None:
            logger.error("stderr read error no: %s" % error)
            pipe_handle.close()
        else:
            self.on_log_update(self.inst_id, PipeNo.STDERR, data.decode())

    # TODO
    def on_terminate(self, timer_handle):
        self._pid = None

    def on_exit(self, proc_handle, status, signal):
        self._pid = None
        # close pipes
        if not self._stdin_pipe.closed:
            self._stdin_pipe.close()
        if not self._stdout_pipe.closed:
            self._stdout_pipe.close()
        if not self._proc.closed:
            self._proc.close()

        inst_daemon = self._proc_pool.get_daemon(self.inst_id)
        inst_daemon.add_crash_count()
        # decr active count
        self._proc_pool.decr_active_count()

        self.on_instance_stop(self.inst_id, status, signal)

    def load_config(self, mc_w_config):
        self._proc_config = mc_w_config

    def _start_process_async(self, async_handle):
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

        # init pipes
        self._stdin_pipe = pyuv.Pipe(self._loop, True)
        self._stdout_pipe = pyuv.Pipe(self._loop, True)
        self._stderr_pipe = pyuv.Pipe(self._loop, True)

        # set pipes
        stdin  = pyuv.StdIO(stream=self._stdin_pipe, flags=pyuv.UV_CREATE_PIPE | pyuv.UV_READABLE_PIPE)
        stdout = pyuv.StdIO(stream=self._stdout_pipe, flags=pyuv.UV_CREATE_PIPE | pyuv.UV_WRITABLE_PIPE)
        stderr = pyuv.StdIO(stream=self._stderr_pipe, flags=pyuv.UV_CREATE_PIPE | pyuv.UV_WRITABLE_PIPE)

        # spawn process
        self._proc = pyuv.Process.spawn(self._loop,
                                  args=cmd_args,
                                  exit_callback=self.on_exit,
                                  stdio=[stdin, stdout, stderr],
                                  cwd=mc_w_config.proc_cwd,
                                  flags=pyuv.UV_PROCESS_DETACHED)
        # set pid
        self._pid = self._proc.pid
        logger.info("Start Process pid=(%s)" % self._pid)

        # on read
        self._stdout_pipe.start_read(self.on_stdout_read)
        self._stderr_pipe.start_read(self.on_stderr_read)

        # incr active count, reset crash count, run callbacks and so on
        self._proc_pool.incr_active_count()
        logger.debug("active count = %s" % self._proc_pool.get_active_count())

        # run callback
        self.on_instance_start(self.inst_id)
        return True

    def start_process(self):
        self.async = pyuv.Async(self._loop, self._start_process_async)
        self.async.send()

    def stop_process(self):
        if self._pid != None:
            logger.info("kill process pid=(%s)" % self._pid)
            self.send_command("stop")
        else:
            logger.error("Kill process failed!")

    # Stop the process brutally
    # It's used when no response even prompting `stop` command
    # Notice, this method is only for emergency usage,
    # It won't give MC processes enough time to save world.
    def terminate_process(self):
        if self.get_pid() != None:
            # kill -9 <pid>
            os.kill(self.get_pid(), 9)
        else:
            logger.error("Terminate process failed!")

    def send_command(self, command):
        _command = (command + "\n").encode()
        logger.debug("write command: %s" % command)
        if not self._stdin_pipe.closed:
            self._stdin_pipe.write(_command)

    def get_pid(self):
        return self._pid
