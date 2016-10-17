from circus.client import CircusClient

class SystemProcessClient(CircusClient):
    '''
    Mainly manage web and ftp process
    In the future, we will consider adding Minecraft process monitoring
    '''
    def __init__(self):
        CircusClient.__init__(self, timeout=0.5)

    def send_msg(self,command, props=None):
        msg_json = {"command": command, "properties": props or {}}

        return self.call(msg_json)

    def send_restart_cmd(self, watcher_name, waiting=True):
        '''
        ZeroMQ message
        {
            "command": "restart",
            "properties": {
                "name": "<name>",
                "waiting": False,
                "match": "[simple|glob|regex]"
            }
        }
        :param watcher_name:
        :return:
        '''
        props = {
            "name" : watcher_name,
            "waiting" : waiting,
            "match":"simple"
        }
        self.send_msg("restart", props)
