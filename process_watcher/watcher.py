__author__ = "Nigshoxiz"

from . import logger, SERVER_STATE, Singleton
from .process_pool import MCProcessPool
from .process import MCProcess
from .daemon_manager import MCDaemonManager
from .instance_info import MCInstanceInfo
from .mc_config import MCWrapperConfig
from .process_callback import MCProcessCallback

from app.controller.global_config import GlobalConfig

import pyuv, os, threading, math

class Watcher(metaclass=Singleton):
    def __init__(self):
        self._loop = pyuv.Loop()
        """
        Is Event Loop running?
        If not, and _active_count > 0 (i.e. some processes need loop to handle!)
        Just create a thread execute `loop.run()`
        """
        self._loop_running = False

        self.proc_pool = MCProcessPool()
        self.callback  = MCProcessCallback()
        self._init_proc_pool()
        pass

    def _init_proc_pool(self):
        gc = GlobalConfig()

        # first, we have to make sure that database has been
        # initialized.
        if gc.get("init_super_admin") == True:
            # import dependencies here to prevent circular import
            from app import db
            from app.model import ServerInstance, JavaBinary, ServerCORE

            # search
            _q = db.session.query(ServerInstance).join(JavaBinary).join(ServerCORE).all()
            if _q == None:
                return None
            for item in _q:
                # init config
                mc_w_config = {
                    "jar_file": os.path.join(item.ob_server_core.file_dir, item.ob_server_core.file_name),
                    "java_bin": item.ob_java_bin.bin_directory,
                    "max_RAM": int(item.max_RAM),
                    "min_RAM": math.floor(int(item.max_RAM) / 2),
                    "proc_cwd": item.inst_dir,
                    "port": item.listening_port
                }

                info = {
                    "total_RAM": item.max_RAM,
                    "total_player": item.max_user,
                    "owner": item.owner_id
                }

                # adding initial data into proc_pool
                _model = {
                    "config" : MCWrapperConfig(**mc_w_config),
                    "status" : SERVER_STATE.HALT,
                    "daemon" : MCDaemonManager(item.auto_restart),
                    "info"   : MCInstanceInfo(**info),
                    "proc"   : MCProcess(item.inst_id, self._loop)
                }
                self.proc_pool.add(item.inst_id, _model)
            return True
        else:
            return None

    def _launch_loop(self):
        def _run_loop():
            self._loop_running = True
            self._loop.run()
            # after all processes finish
            self._loop_running = False

        if self.proc_pool.get_active_count() > 0 and self._loop_running == False:
            t = threading.Thread(target=_run_loop)
            t.setDaemon(True)
            t.start()

    def start_instance(self, inst_id):
        inst_obj = self.proc_pool.get(inst_id)

        if inst_obj == None:
            return None
        _proc    = inst_obj.get("proc")
        _status  = inst_obj.get("status")
        _daemon  = inst_obj.get("daemon")
        mc_w_config  = inst_obj.get("config")

        # reload config
        _proc.load_config(mc_w_config)

        # make sure status is HALT, or just skip it because
        # there's already an running instance.
        if _status != SERVER_STATE.HALT:
            return None

        # start process
        if _proc.start_process():
            # add active count
            self.proc_pool.incr_active_count()

            logger.debug("active count = %s, running = %s" % (self.proc_pool.get_active_count(), self._loop_running))
            # set status
            # TODO add callback
            # loop.run
            self._launch_loop()

            # reset daemon
            _daemon.reset_crash_count()
            self.callback.on_instance_start(inst_id)

    def stop_instance(self, inst_id):
        inst_obj = self.proc_pool.get(inst_id)

        if inst_obj == None:
            return None
        _proc    = inst_obj.get("proc")
        _status  = inst_obj.get("status")

        # the stop callback shall do the work of marking the new status (HALT)
        # and deduct active count. Don't do them HERE!
        _proc.stop_process()

    def send_command(self, inst_id, command):
        inst_obj = self.proc_pool.get(inst_id)

        if inst_obj == None:
            return None
        _proc    = inst_obj.get("proc")
        _status  = inst_obj.get("status")

        # limit max command length to send
        if _status == SERVER_STATE.RUNNING and len(command) < 10000:
            _proc.send_command(command)
