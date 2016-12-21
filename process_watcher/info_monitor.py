from . import Singleton, logger, SERVER_STATE
from .process_callback import MCProcessCallback
from .process_pool import MCProcessPool

import psutil, pyuv
class MCInstanceInfoMonitor(MCProcessCallback):
    def __init__(self, loop):
        MCProcessCallback.__init__(self)
        self.proc_pool = MCProcessPool()
        self._loop = loop
        self.read_memory_timer = pyuv.Timer(self._loop)

    def tick_read_memory(self, timer_handle):
        for inst_id in self.proc_pool.get_insts():
            inst_proc = self.proc_pool.get_proc(inst_id)
            inst_status = self.proc_pool.get_status(inst_id)
            inst_info   = self.proc_pool.get_info(inst_id)

            if inst_status == SERVER_STATE.RUNNING:
                try:
                    pid = inst_proc.get_pid()
                    proc_info = psutil.Process(pid)
                    memory = proc_info.memory_info()[0] / float(2 ** 20) # unit: MB
                except:
                    memory = None
                finally:
                    if memory != None:
                        inst_info.set_RAM(memory)
                        self.on_memory_change(inst_id, memory)

    def start_timer(self, interval = 5.0):
        if not self.read_memory_timer.active:
            self.read_memory_timer.start(self.tick_read_memory, 0.0, interval)

'''
MC socket code:
                    self.socket = MCSocket()
                    self.socket.connect(port)
                    self.add_f(self.socket.sock, POLL_IN | POLL_HUP)
                    # Minecraft PING command
                    self.socket.send_data(b'\x00\x00', "127.0.0.1", port, b'\x01')
                    self.socket.send_data(b'\x00')

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
                    logger.debug(traceback.format_exc())
                    return None

'''
