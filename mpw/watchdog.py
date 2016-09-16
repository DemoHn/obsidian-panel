__author__ = "Nigshoxiz"

from .instance import MCServerInstance
from . import event_loop, logger

import threading

class Watchdog(object):
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
        pass

    def _handle_log(self, events):
        for sock, fd, event in events:
            

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
            "config" : config,
            "port" : _port,
            "inst" : MCServerInstance(_port)
        }

        self.proc_pool[_inst_key] = _inst_val
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
        pass

    def stop_instance(self, inst_id):
        pass

    def launch(self):
        def _launch_loop():
            event_loop.run()

        t = threading.Thread(target=_launch_loop)
        t.daemon = True
        t.start()
        logger.info("start Watchdog thread.")

    def terminate(self):
        # set stopping to True -> terminate while loop
        event_loop.stopping = True
        logger.info("stop Watchdog thread.")