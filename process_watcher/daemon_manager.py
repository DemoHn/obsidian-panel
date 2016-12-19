class MCDaemonManager(object):
    MAX_CRASH = 5
    def __init__(self, auto_restart=True):
        self.auto_restart = auto_restart
        self._crash_count  = 0

    def add_crash_count():
        self._crash_count += 1
