import os

class MCInstanceInfo(object):

    def __init__(self):
#       self.total_RAM = None
        self.RAM     = None
        self.current_player = None
#        self.total_player = None
        self.log = []
        pass

    def reset(self):
        pass

    def append_log(self, data):
        pass

    def set_RAM(self, RAM):
        self.RAM = RAM

    def set_current_player(self, current_player):
        self.current_player = current_player

    def get_RAM(self):
        return self.RAM

    def get_current_player(self):
        return self.current_player

    def get_log(self):
        pass
