from app.tools.mc_wrapper import MCProcessPool
from app.tools.mc_wrapper.instance import MCServerInstanceThread, MCServerInstance

from app.controller.global_config import GlobalConfig

import copy

gc = GlobalConfig.getInstance()

def start_mc_server(serv_dir, port):
    mc_w_config = {
        "jar_file":"",
        "max_RAM":"",
        "proc_cwd":""
    }
    pass

def stop_mc_server(port):
    mc_pool = MCProcessPool.getInstance()
    mc_pool.get(port).inst.stop_process()
    pass

def restart_mc_server(port):
    pass
