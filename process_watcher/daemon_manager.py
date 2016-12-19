class MCDaemonManager(object):
    MAX_CRASH = 5
    def __init__(self, auto_restart=True):
        self.start_onboot  = auto_restart
        self._crash_count  = 0
        self._restart_flag = True
        self._normal_exit  = False

    def add_crash_count(self):
        if not self._normal_exit:
            self._crash_count += 1
        if self._crash_count > MCDaemonManager.MAX_CRASH:
            self._restart_flag = False

    def reset_crash_count(self):
        if self._crash_count > MCDaemonManager.MAX_CRASH:
            self._crash_count = 0
            self._restart_flag = True

    def set_normal_exit(self, val):
        '''
        when normal_exit is set to True, that means
        the process just closed normally without restart.
        '''
        self._normal_exit = val

        if val == True:
            self._restart_flag = False

    def set_restart_flag(self, val):
        self._restart_flag = val

    def get_normal_exit(self):
        return self._normal_exit

    def get_restart_flag(self):
        return self._restart_flag
