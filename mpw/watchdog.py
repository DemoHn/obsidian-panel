__author__ = "Nigshoxiz"

from . import event_loop, logger, SERVER_STATE
from .instance import MCServerInstance
from .mc_config import MCWrapperConfig

import inspect
import threading

POLL_NULL = 0x00
POLL_IN = 0x01
POLL_OUT = 0x04
POLL_ERR = 0x08
POLL_HUP = 0x10
POLL_NVAL = 0x20

class Watchdog(object):
    instance = None

    def __init__(self):
        '''process pool stores the instance object
        KEY -> "inst_" + <inst id>
        VALUE -> {
            "config" : MC config obj,
            "port" : MC listening port,
            "inst" : MC inst obj,
            "log" : MC running log [array]
        }
        '''
        self.proc_pool = {}

        # hook functions
        # parameters: (<inst_id>, (<param1>, ...))

        # :inst_starting_hook:
        # execute when an instance (that is, a minecraft server) begins initializing
        # Notice, in this situation, players are still waiting for login.
        # additional params:
        # (None)
        self._inst_starting_hook = []

        # :inst_running_hook:
        # execute when an instance finishes initializing.
        # In this situation, players can login to this MC server.
        # additional params:
        # (<init time (sec)>)
        self._inst_running_hook = []

        # :log_update_hook:
        # execute when the server prints new log
        # additional params:
        # (<new log data(string)>)
        self._log_update_hook = []

        # :connection_hook:
        # TODO reserved
        # additional params:
        # (TODO)
        self._connection_lost_hook = []

        # :inst_terminate_hook:
        # execute when server stops running.
        # Can be triggered either by user or by the instance itself (i.e. server crash)
        # additional params:
        # (None)
        self._inst_terminate_hook = []

        # :inst_user_login_hook:
        # execute when new player login the instance
        # additional params:
        # (<user info>)
        self._inst_user_login_hook = []

        # :inst_user_logout_hook:
        # execute when new player logout the instance
        # additional params:
        # (<user info>)
        self._inst_user_logout_hook = []

    @staticmethod
    def getWDInstance():
        if Watchdog.instance == None:
            Watchdog.instance = Watchdog()
        return Watchdog.instance

    def _handle_log(self, events):
        for sock, fd, event in events:
            if event == POLL_IN:
                if sock.closed == False:
                    # get sender by comparing output fd
                    for inst_key in self.proc_pool:
                        inst_obj = self.proc_pool.get(inst_key)
                        _inst = inst_obj["inst"]

                        if fd == _inst._proc.stdout.fileno():
                            log_str = _inst._proc.stdout.read(512)
                            log_arr = log_str.decode('utf-8').split("\n")
                            # append log
                            inst_obj["log"] += log_arr
                            break
                else:
                    logger.warning("pipe socket is closed!")
            else:
                # TODO
                pass

    def _run_hook(self, hook_name, *args):
        _names = ("inst_starting", "inst_running", "log_update",
                  "connection_lost", "inst_terminate", "inst_user_login", "inst_user_logout")

        if hook_name in _names:
            _method = getattr(self, "_%s_hook" % hook_name)

            for _hook_item in _method:
                if inspect.isfunction(_hook_item):
                    _hook_item(*args)

    def register_instance(self, inst_id, port, config):
        '''
        register a new instance to the process pool, which manages all minecraft processes.
        :param inst_id:
        :param port:
        :param config:
        :return:
        '''
        _port = int(port)
        _inst_key = "inst_" + str(inst_id)
        _inst_val = {
            "config" : MCWrapperConfig(**config), # READ_ONLY
            "port" : _port, # READ_ONLY
            "inst" : None, #MCServerInstance(_port),
            "log" : []
        }

        _k = self.proc_pool.get(_inst_key)
        print(_k)
        if _k != None:
            if _k.get("inst") == None:
                _k["inst"] = MCServerInstance(_port)
        else:
            self.proc_pool[_inst_key] = _inst_val
            self.proc_pool[_inst_key]["inst"] = MCServerInstance(_port)
        return True

    def add_instance(self, inst_id, port, config):
        '''
        just an alias of method `register_instance`
        '''
        return self.register_instance(inst_id, port, config)

    def del_instance(self, inst_id):
        '''
        Delete instance from the world.
        Be really CAREFUL, it may lost everything!
        :param inst_id:
        :return:
        '''
        _inst_key = "inst_" + str(inst_id)
        if self.proc_pool.get(_inst_key) != None:
            del self.proc_pool[_inst_key]

    def start_instance(self, inst_id):
        _inst_key = "inst_" + str(inst_id)
        _inst_conf = self.proc_pool.get(_inst_key)

        _inst = _inst_conf.get("inst")
        _config = _inst_conf.get("config")
        if _inst == None:
            raise Exception("Instance is None!")
        else:
            if _inst._status == SERVER_STATE.HALT:
                _inst.start_process(_config)

    def stop_instance(self, inst_id):
        _inst_key = "inst_" + str(inst_id)
        _inst_profile = self.proc_pool.get(_inst_key)

        _inst = _inst_profile.get("inst")
        if _inst == None:
            raise Exception("Instance is None!")
        else:
            if _inst._status == SERVER_STATE.RUNNING \
                    or _inst._status == SERVER_STATE.STARTING:
                # TODO
                _inst.stop_process()

    def get_instance(self, inst_id):
        _inst_key = "inst_" + str(inst_id)
        if self.proc_pool.get(_inst_key) == None:
            return None
        else:
            return self.proc_pool.get(_inst_key).get("inst")

    def launch(self):
        def _launch_loop():
            event_loop.run()

        # before start
        event_loop.add_handler(self._handle_log)
        event_loop.stopping = False
        t = threading.Thread(target=_launch_loop)
        t.daemon = True
        t.start()
        logger.info("start Watchdog thread.")

    def terminate(self):
        # set stopping to True -> terminate while loop
        event_loop.stopping = True
        logger.info("stop Watchdog thread.")