__author__ = "Nigshoxiz"

import asyncio
import threading
import traceback

from mc_wrapper import MCWrapperConfig, MCProcessPool
from mc_wrapper import logger
from mc_wrapper.server_log import LogMonitorProtocol

import os
from app.tools.mc_wrapper.server_properties_parser import ServerPropertiesParser


class MCServerInstance():
    STATE_HALT = 0
    STATE_STARTING = 1
    STATE_RUNNING = 2
    def __init__(self, port, loop=None):

        if loop == None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

        self.port = port

        # init pid
        self._pid = 0
        self._status = MCServerInstance.STATE_HALT
        self.transport = None
        self.process   = None

    def init_env(self,proc_cwd):
        # init eula.txt
        EULA_txt_file = os.path.join(proc_cwd, "eula.txt")
        if not os.path.isfile(EULA_txt_file):
            # write eula=true into the eula file , or the server process will refuse to start.
            f = open(EULA_txt_file, "w+")
            f.write("eula=true")
            f.close()

        # init server.properties
        s_p_file = os.path.join(proc_cwd,"server.properties")

        if not os.path.isfile(s_p_file):
            open(s_p_file,"a").close()

        parser = ServerPropertiesParser(s_p_file)
        parser.set_server_port(self.port)
        # write config to the file
        parser.dumps()

    # @params
    # mc_w_config : just an instance of class MCWrapperConfig()
    def start_process(self, mc_w_config):

        cmd = mc_w_config.java_bin
        cmd_args = ["-Xms%sM" % int(float(mc_w_config.min_RAM) * 1024),
                    "-Xmx%sM" % int(float(mc_w_config.max_RAM) * 1024),
                    "-jar",
                    mc_w_config.jar_file,
                    "nogui"]

        logger.info("start process %s", cmd + " " +" ".join(cmd_args))

        self.init_env(mc_w_config.proc_cwd)
        transport , process = self.loop.run_until_complete(
            # loop.subprocess_exec(<proc_factory>,cmd, *cmd_args, cwd = mc_w_config.proc_cwd)
            # self.loop.subprocess_exec(asyncio.SubprocessProtocol,cmd, *cmd_args, cwd = mc_w_config.proc_cwd)
            self.loop.subprocess_exec(lambda: LogMonitorProtocol(str(self.port)), cmd, *cmd_args, cwd = mc_w_config.proc_cwd)
        )
        self._pid = transport.get_pid()
        logger.debug("PID = %s" % self._pid)
        if self._pid != 0:
            self._status = MCServerInstance.STATE_STARTING

        self.transport = transport
        self.process   = process

    def stop_process(self):
        if self._pid > 0:
            logger.info("kill process PID %s" % self._pid)

            self.send_command("stop")
            # wait for completion of child process. To avoid zombie process.
            try:
                #_pid, _status = os.waitpid(self._pid,0)
                #yield from self.process.wait()
                print("end")
                # terminate the thread

            except OSError:
                traceback.print_exc()
            #threading.current_thread().stop()
        else:
            logger.error("Kill Process Falied! PID value is None!")

    # send command
    def send_command(self,command):
        pipe = self.transport.get_pipe_transport(0)

        if pipe == None:
            logger.debug("pipe is undefined! Maybe the process is still not created?")
        else:
            _command = (command + "\n").encode("utf-8")
            logger.debug("Write command : "+command)
            pipe.write(_command)

    # callbacks
    # TODO implement them
    def user_login_callback(self):
        pass

    def user_exit_callback(self):
        pass

    def terminate_callback(self):
        logger.info("Process %s exit. Port is %s." % (self._pid, self.port))
        self._status = MCServerInstance.STATE_HALT
        self.loop.stop()

class MCServerInstanceThread(threading.Thread):
    def __init__(self, port, config=None):
        super(MCServerInstanceThread,self).__init__(kwargs = config)
        self._loop = asyncio.new_event_loop()
        self.port  = port

    def run(self):
        """
        create MC server process
        :return:
        """
        port    = self.port
        mc_pool = MCProcessPool.getInstance()
        # init lock
        if mc_pool.lock_exists(port):
            logger.warning("A process is alreay running on port %s!" % port)
        else:
            mc_pool.add_lock(port)

        # init loop
        conf_kwargs = self._kwargs
        loop = self._loop
        asyncio.set_event_loop(loop)

        # init MC config
        config = MCWrapperConfig(**conf_kwargs)


        # init ServerInstance
        inst = MCServerInstance(port, loop = loop)

        # add instance to instance_pool
        mc_pool.add(port,inst)

        # start process
        inst.start_process(config)

        loop.run_forever()
        loop.close()

        # after the process quit, delete the server instance from instance pool.
        MCProcessPool.getInstance().remove(port)
        mc_pool.del_lock(port)
        logger.debug("terminate thread %s" % threading.current_thread())