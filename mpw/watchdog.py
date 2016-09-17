__author__ = "Nigshoxiz"

from . import event_loop, SERVER_STATE
from .instance import MCServerInstance
from .mc_config import MCWrapperConfig

import re
import inspect
import threading
import logging

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
            "log" : MC running log,
            "current_user" : 0
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

        # :inst_player_login_hook:
        # execute when new player login the instance
        # additional params:
        # (<current online players num>,<player info>)
        self._inst_player_login_hook = []

        # :inst_player_logout_hook:
        # execute when new player logout the instance
        # additional params:
        # (<current online players num>,<player info>)
        self._inst_player_logout_hook = []

        # :inst_player_change_hook:
        # execute when online players' number changed
        # additional params:
        # (<current online players>)
        self._inst_player_change_hook = []

    @staticmethod
    def getWDInstance():
        if Watchdog.instance == None:
            Watchdog.instance = Watchdog()
        return Watchdog.instance

    def _run_hook(self, hook_name, inst_id, args_tuple):
        _names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout", "inst_player_change")

        if hook_name in _names:
            _method = getattr(self, "_%s_hook" % hook_name)

            for _hook_item in _method:
                if inspect.isfunction(_hook_item) or inspect.ismethod(_hook_item):
                    _hook_item(inst_id, args_tuple)

    def _event_handler(self, events):
        '''
        handling events triggered in event loop
        :param events:
        :return:
        '''
        def _run_hooks_by_log(inst_id, log_str, inst):
            '''
            run hooks when log updated.
            :param inst_id: instance id
            :param log_str: new log (utf-8 string)
            :param inst: MC instance <mpw.MCServerInstance>
            :return:
            '''
            self._run_hook("log_update", inst_id, (log_str))
            # find keyword Done in the new log
            re_done_str = "Done \(([0-9.]+)s\)!"

            if re.search(re_done_str, log_str) != None \
                and inst._status == SERVER_STATE.STARTING: # prevent misjudgement by player inputting 'Done'

                m = re.search(re_done_str, log_str)
                init_span = 0.0
                try:
                    init_span = float(m.group(1))
                except:
                    init_span = -1.0
                finally:
                    inst._status = SERVER_STATE.RUNNING
                    self._run_hook("inst_running", inst_id, (init_span))
                    # TEST stop
                    #inst.stop_process()

        for sock, fd, event in events:
            if event == POLL_IN:
                #if sock.closed == False:
                if True:
                    # get sender by comparing output fd
                    for inst_key in self.proc_pool:
                        inst_obj = self.proc_pool.get(inst_key)
                        _inst = inst_obj["inst"]

                        if fd == _inst._proc.stdout.fileno():
                            line = _inst._proc.stdout.readline()
                            log_str = line.decode('utf-8')
                            # append log
                            inst_obj["log"] += log_str
                            inst_id = int(inst_key[5:])
                            _run_hooks_by_log(inst_id, log_str, _inst)
                            break
                else:
                    logging.warning("pipe socket is closed!")
            # when connection terminate, this branch will start
            elif event == POLL_HUP:
                for inst_key in self.proc_pool:
                    inst_obj = self.proc_pool.get(inst_key)
                    _inst = inst_obj["inst"]

                    if fd == _inst._proc.stdout.fileno():
                        inst_id = int(inst_key[5:])
                        # run hook
                        self._run_hook("inst_terminate", inst_id, (None))

                        # remove this fd from event loop
                        # or there will be endless trigger for POLL_HUP
                        _proc_stdout = _inst._proc.stdout
                        event_loop.remove(_proc_stdout)

                        # remove instance
                        inst_obj["inst"] = None

    def add_hook(self, hook_name, fn):
        '''
        add
        :param hook_name:
        :param fn: function to execute.
        each hook function should define 2 input parameters
        (one for inst_id, another one for additional arguments defined as an tuple)
        e.g. :
        def hook_func(inst_id, arg_tuple):
            ****
            pass

        :return:
        '''
        _names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout", "inst_player_change")

        if hook_name in _names:
            _method = getattr(self, "_%s_hook" % hook_name)

            if inspect.isfunction(fn) or inspect.ismethod(fn):
                _method.append(fn)

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
            "log" : "",
            "current_user" : 0,
            "inst": None,  # MCServerInstance(_port),
        }

        _k = self.proc_pool.get(_inst_key)
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
                pid = _inst.start_process(_config)
                if pid != None:
                    self._run_hook("inst_starting", inst_id, (None))

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

    def send_command(self, inst_id, command):
        '''
        send MC command to MC instance
        :param inst_id:
        :return:
        '''
        _inst_key = "inst_" + str(inst_id)
        if self.proc_pool.get(_inst_key) == None:
            return None
        else:
            _inst = self.proc_pool.get(_inst_key).get("inst")
            _inst.send_command(command)

    def launch(self, hook_class = None):
        def _launch_loop():
            event_loop.run()

        # add hook
        if hook_class != None:
            if inspect.isclass(hook_class):
                # init it
                hook_class(self.add_hook)

        # before start
        event_loop.add_handler(self._event_handler)
        event_loop.stopping = False
        t = threading.Thread(target=_launch_loop)
        t.daemon = True
        t.start()
        logging.info("start Watchdog thread.")

    def terminate(self):
        # set stopping to True -> terminate while loop
        event_loop.stopping = True
        logging.info("stop Watchdog thread.")