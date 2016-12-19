import os

class MCInstanceInfo(object):

    def __init__(self, total_RAM=None,total_player=None, owner=None):
        self.total_RAM = total_RAM
        self.RAM     = None
        self.current_player = None
        self.total_player = total_player
        self.owner = owner
        self.log = []
        # TODO
        self.player_dict = {}
        pass

    def reset(self):
        self.RAM = None
        self.current_player = None

    def append_log(self, data):
        pass

    def set_RAM(self, RAM):
        self.RAM = RAM

    def set_current_player(self, current_player):
        self.current_player = current_player

    def incr_current_player(self):
        if self.current_player == None:
            self.current_player = 0
        self.current_player += 1

    def decr_current_player(self):
        if self.current_player == None:
            self.current_player = 0
        self.current_player -= 1

    def get_RAM(self):
        return self.RAM

    def get_current_player(self):
        return self.current_player

    def get_owner(self):
        return self.owner

    def get_total_player(self):
        return self.total_player

    def get_total_RAM(self):
        return self.total_RAM

    def get_log(self):
        pass
