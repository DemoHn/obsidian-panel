import re

from . import logger, Singleton, SERVER_STATE
from .process_pool import MCProcessPool

from app.tools.mq_proxy import WS_TAG, MessageQueueProxy

class MCProcessCallback():
    def __init__(self):
        self._proc_pool = MCProcessPool()

    # event name : inst_event
    def broadcast(self, inst_id, event_name, value):
        proxy = MessageQueueProxy(WS_TAG.MPW)
        event_prefix = "process"
        event_type = "broadcast"

        _name = "%s.%s" % (event_prefix, event_type)
        values = {
            "inst_id": inst_id,
            "event": event_name,
            "val": value
        }
        _info = self._proc_pool.get_info(inst_id)
        uid   = _info.get_owner()
        proxy.send(None, _name, values, WS_TAG.CONTROL, uid=uid)

    def on_log_update(self, inst_id, pipe, log):
        # broadcast raw log
        # TODO handle different situation
        self._log_string_analyse(inst_id, log)
        self.broadcast(inst_id, "log_update", log)

    def on_instance_start(self, inst_id):
        self._proc_pool.set_status(inst_id, SERVER_STATE.STARTING)
        self.broadcast(inst_id, "status_change", SERVER_STATE.STARTING)

    def on_instance_running(self, inst_id, start_time):
        self._proc_pool.set_status(inst_id, SERVER_STATE.RUNNING)
        self.broadcast(inst_id, "status_change", SERVER_STATE.RUNNING)

    def on_instance_stop(self, inst_id, status, signal):
        self._proc_pool.set_status(inst_id, SERVER_STATE.HALT)
        self.broadcast(inst_id, "status_change", SERVER_STATE.HALT)

        # if restart is asked
        inst_daemon = self._proc_pool.get_daemon(inst_id)
        inst_proc   = self._proc_pool.get_proc(inst_id)
        inst_config = self._proc_pool.get_config(inst_id)

        if inst_daemon.get_restart_flag():
            logger.debug("restart inst (%s)" % inst_id)

            # reload config and start again
            inst_proc.load_config(inst_config)
            inst_proc.start_process()

        inst_daemon.set_restart_flag(True)
        inst_daemon.set_normal_exit(False)

    def on_instance_unexpectedly_exit(self, inst_id):
        pass

    def on_player_login(self, inst_id, player_info):
        inst_info = self._proc_pool.get_info(inst_id)
        self.broadcast(inst_id, "player_change", inst_info.get_current_player())

    def on_player_logout(self, inst_id, player_info):
        inst_info = self._proc_pool.get_info(inst_id)
        self.broadcast(inst_id, "player_change", inst_info.get_current_player())

    def on_player_leave(self, inst_id, player):
        # TODO how to define `leave`?
        pass

    def on_player_change(self, inst_id, player_num):
        self.broadcast(inst_id, "player_change", player_num)
        pass

    def on_memory_change(self, inst_id, memory):
        self.broadcast(inst_id, "memory_change", memory)
        pass

    def _log_string_analyse(self, inst_id, log_str):
        '''
        run hooks when log updated.
        :param inst_id: instance id
        :param log_str: new log (utf-8 string)
        :return:
        '''
        # find keyword Done in the new log
        re_done_str = "Done \(([0-9.]+)s\)!"
        re_login_str = "^\[\d\d:\d\d:\d\d INFO\]: (.*)\[(.*)\] logged in"
        re_logout_str = "^\[\d\d:\d\d:\d\d INFO\]: (.*) left the game"
        re_UUID_str = "UUID of player (.*) is (.*)"
        re_online_user_str = "There are ([0-9]+)/([0-9]+) players"

        if re.search(re_done_str, log_str) != None \
                and self._proc_pool.get_status(inst_id) == SERVER_STATE.STARTING:  # prevent misjudgement by player inputting 'Done'

            m = re.search(re_done_str, log_str)
            start_time = 0.0
            try:
                start_time = float(m.group(1))
            except:
                start_time = -1.0
            finally:
                self._proc_pool.set_status(inst_id, SERVER_STATE.RUNNING)
                self.on_instance_running(inst_id, start_time)
        # user login
        elif re.search(re_login_str, log_str) != None \
                and self._proc_pool.get_status(inst_id) == SERVER_STATE.RUNNING:

            m = re.search(re_login_str, log_str)
            player_name = m.group(1)
            player_ip = m.group(2)

            _info = self._proc_pool.get_info(inst_id)
            _info.incr_current_player()
            self.on_player_login(inst_id, (player_name, player_ip))
#            self._run_hook("inst_player_login", inst_id, (player_name, player_UUID, player_ip, u["current_player"]))
        # user logout
        elif re.search(re_logout_str, log_str) != None \
                and self._proc_pool.get_status(inst_id) == SERVER_STATE.RUNNING:

            m = re.search(re_logout_str, log_str)
            player_name = m.group(1)

            _info = self._proc_pool.get_info(inst_id)
            _info.decr_current_player()
            self.on_player_logout(inst_id, (player_name))

            #self._run_hook("inst_player_logout", inst_id, (player_name, player_UUID, u["current_player"]))
        # bind UUID
        elif re.search(re_UUID_str, log_str) != None \
                and self._proc_pool.get_status(inst_id) == SERVER_STATE.RUNNING:
            pass
            #m = re.search(re_UUID_str, log_str)
            #player_name = m.group(1)
            #player_UUID = m.group(2)

            # register UUID of a player
            #self.__UUID_dict[player_name] = player_UUID

            # elif re.search(re_online_user_str, log_str) != None \
            #    and inst.get_status() == SERVER_STATE.RUNNING:
            #
            #    m = re.search(re_online_user_str, log_str)
            #    online_player = m.group(1)
            #    total_player  = m.group(2)
            #
            #   self._run_hook("inst_player_change", inst_id, (online_player, total_player))
