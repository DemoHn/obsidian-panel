__author__ = "Nigshoxiz"

from . import event_loop, SERVER_STATE
from .instance import MCServerInstance
from .mc_config import MCWrapperConfig
from .mc_socket import MCSocket

# scheduler
from apscheduler.schedulers.background import BackgroundScheduler

import re
import inspect
import threading
import logging
import psutil
import json
import traceback
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
            "current_player" : 0
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

        # :inst_memory_change_hook:
        # execute when allocated memory changes
        # additional params:
        # (<current allocated memory on this inst>)
        self._inst_memory_change_hook = []

        self._hook_names = ("inst_starting", "inst_running",
                  "log_update",
                  "connection_lost", "inst_terminate",
                  "inst_player_login", "inst_player_logout",
                  "inst_player_change","inst_memory_change")

        # stores UUID
        self.__UUID_dict = {}

        # scheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self._schedule_read_memory,'interval', seconds = 5)
        self.scheduler.add_job(self._schedule_check_online_user,'interval', seconds=60)

        # socket
        self.socket = MCSocket()

    @staticmethod
    def getWDInstance():
        if Watchdog.instance == None:
            Watchdog.instance = Watchdog()
        return Watchdog.instance

    def _schedule_read_memory(self):
        for inst_key in self.proc_pool:
            inst_dict = self.proc_pool.get(inst_key)
            inst_id = int(inst_key[5:])
            inst = inst_dict.get("inst")

            mem = None
            try:
                pid = inst.get_pid()
                process = psutil.Process(pid)
                mem = process.memory_info()[0] / float(2 ** 20) # unit : MiB
            except:
                mem = None
            finally:
                if mem != None and inst != None:
                    if inst.get_status() == SERVER_STATE.RUNNING:
                        self._run_hook("inst_memory_change", inst_id, (mem))

    def _schedule_check_online_user(self):
        for inst_key in self.proc_pool:
            inst_dict = self.proc_pool.get(inst_key)

            inst = inst_dict.get("inst")

            if inst != None:
                if inst.get_status() == SERVER_STATE.RUNNING:
                    # just send command, hook will be triggered after results shows
                    #inst.send_command("list")
                    port = int(inst.port)
                    self.socket = MCSocket()
                    self.socket.connect(port)
                    event_loop.add(self.socket.sock, POLL_IN | POLL_HUP)
                    # Minecraft PING command
                    self.socket.send_data(b'\x00\x00', "127.0.0.1", port, b'\x01')
                    self.socket.send_data(b'\x00')

    def _run_hook(self, hook_name, inst_id, args_tuple):
        _names = self._hook_names

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
            re_login_str = "^\[\d\d:\d\d:\d\d INFO\]: (.*)\[(.*)\] logged in"
            re_logout_str = "^\[\d\d:\d\d:\d\d INFO\]: (.*) left the game"
            re_UUID_str = "UUID of player (.*) is (.*)"
            re_online_user_str = "There are ([0-9]+)/([0-9]+) players"

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
            # user login
            elif re.search(re_login_str, log_str) != None \
                    and inst.get_status() == SERVER_STATE.RUNNING:

                m = re.search(re_login_str, log_str)
                player_name = m.group(1)
                player_ip = m.group(2)

                player_UUID = self.__UUID_dict.get(player_name)

                # inc current user num
                _inst_key = "inst_" + str(inst_id)
                u = self.proc_pool.get(_inst_key)
                u["current_player"] += 1

                self._run_hook("inst_player_login", inst_id, (player_name, player_UUID, player_ip, u["current_player"]))
            # user logout
            elif re.search(re_logout_str, log_str) != None \
                and inst.get_status() == SERVER_STATE.RUNNING:

                m = re.search(re_logout_str, log_str)
                player_name = m.group(1)
                player_UUID = self.__UUID_dict.get(player_name)

                # dec current user num
                _inst_key = "inst_" + str(inst_id)
                u = self.proc_pool.get(_inst_key)
                u["current_player"] -= 1

                self._run_hook("inst_player_logout", inst_id, (player_name, player_UUID, u["current_player"]))
            # bind UUID
            elif re.search(re_UUID_str, log_str) != None \
                and inst.get_status() == SERVER_STATE.RUNNING:

                m = re.search(re_UUID_str, log_str)
                player_name = m.group(1)
                player_UUID = m.group(2)

                # register UUID of a player
                self.__UUID_dict[player_name] = player_UUID

            #elif re.search(re_online_user_str, log_str) != None \
            #    and inst.get_status() == SERVER_STATE.RUNNING:
            #
            #    m = re.search(re_online_user_str, log_str)
            #    online_player = m.group(1)
            #    total_player  = m.group(2)
            #
            #   self._run_hook("inst_player_change", inst_id, (online_player, total_player))

        def _run_hooks_by_sock(inst_id, sock_data, inst):
            # find packet id
            # check http://wiki.vg/Server_List_Ping for minecraft protocol details
            pack_length = sock_data[0]
            pack_id = sock_data[1]
            # Minecraft PING response
            if pack_id == 0x00:
                # TODO compatible for old versions' protocol
                json_length = sock_data[2]
                json_str   = (sock_data[3:]).decode("utf-8")

                try:
                    dict = json.loads(json_str)
                    current_player = dict.get("players").get("online")
                    total_player   = dict.get("players").get("max")
                    # modify inst data
                    inst_key = "inst_%s" % inst_id
                    inst_dict = self.proc_pool.get(inst_key)
                    inst_dict["current_player"] = current_player
                    self._run_hook("inst_player_change", inst_id, (current_player, total_player))
                except:
                    logging.debug(traceback.format_exc())
                    return None

        for sock, fd, event in events:
            if event == POLL_IN:
                #if sock.closed == False:
                if sock == self.socket.sock:
                    # minecraft ping protocol
                    # read sock data
                    server_ip, server_port = sock.getpeername()
                    try:
                        chunk = self.socket.sock.recv(4096)
                    finally:
                        event_loop.remove(sock)
                        self.socket.sock.close()

                    bin_data = chunk
                    # find instance correspond to peer port
                    for inst_key in self.proc_pool:
                        inst_dict = self.proc_pool.get(inst_key)
                        _port = inst_dict.get("port")

                        inst_id = int(inst_key[5:])

                        inst    = inst_dict.get("inst")
                        if _port == server_port:
                            if inst != None:
                                _run_hooks_by_sock(inst_id, bin_data, inst)
                                break

                else:
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

            # when connection terminate, this branch will start
            elif event == POLL_HUP:
                if sock == self.socket.sock:
                    event_loop.remove(sock)
                else:
                    # pipe event
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

                            # reset instance object dict
                            inst_obj["inst"] = None
                            inst_obj["current_player"] = 0

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
        _names = self._hook_names

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
            "current_player" : 0,
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

    def reset_instance(self, inst_id, port, config):
        self.del_instance(inst_id)
        self.register_instance(inst_id, port, config)

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
            if _inst != None and _inst.get_status() == SERVER_STATE.RUNNING:
                _inst.send_command(command)

    def read_log(self, inst_id):
        _inst_key = "inst_" + str(inst_id)
        if self.proc_pool.get(_inst_key) == None:
            return None
        else:
            _log = self.proc_pool.get(_inst_key).get("log")
            return _log

    def launch(self, hook_class = None):
        def _launch_loop():
            event_loop.run()

        # add hook
        if hook_class != None:
            if inspect.isclass(hook_class):
                # init it
                hook_class(self)

        # before start
        event_loop.add_handler(self._event_handler)
        event_loop.stopping = False
        t = threading.Thread(target=_launch_loop)
        t.daemon = True
        t.start()

        # start scheduler
        self.scheduler.start()
        logging.info("start Watchdog thread.")

    def terminate(self):
        # set stopping to True -> terminate while loop
        event_loop.stopping = True
        self.scheduler.shutdown()
        logging.info("stop Watchdog thread.")
