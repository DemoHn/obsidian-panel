import logging, datetime, json, sys
from logging import Formatter
# ref : http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python

global loggers
loggers = {}

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    WHITE = '\033[97m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def format_header(str):
        return "%s%s%s" % (Colors.HEADER, str, Colors.ENDC)

    @staticmethod
    def format_blue(str):
        return "%s%s%s" % (Colors.OKBLUE, str, Colors.ENDC)

    @staticmethod
    def format_underline(str):
        return "%s%s%s" % (Colors.UNDERLINE, str, Colors.ENDC)

    @staticmethod
    def format_green(str):
        return "%s%s%s" % (Colors.OKGREEN, str, Colors.ENDC)

    @staticmethod
    def format_warning(str):
        return "%s%s%s" % (Colors.WARNING, str, Colors.ENDC)

    @staticmethod
    def format_fail(str):
        return "%s%s%s" % (Colors.FAIL, str, Colors.ENDC)

    @staticmethod
    def format_bold(str):
        return "%s%s%s" % (Colors.BOLD, str, Colors.ENDC)

    @staticmethod
    def format_white(str):
        return "%s%s%s" % (Colors.WHITE, str, Colors.ENDC)

class ObsidianDebugFormatter(Formatter):
    def __init__(self, task_name=None):
        self.task_name = task_name

        super(ObsidianDebugFormatter, self).__init__()

    def format(self, record):

        def _format_title(levelno, dt_str):
            map = {
                logging.DEBUG: Colors.format_green("[D %s]" % dt_str),
                logging.INFO: Colors.format_header("[I %s]" % dt_str),
                logging.WARN: Colors.format_warning("[W %s]" % dt_str),
                logging.ERROR: Colors.format_fail("[E %s]" % dt_str),
                logging.CRITICAL: Colors.format_fail("[C %s]" % dt_str)
            }
            return map[levelno]

        dt_str = datetime.datetime.now().strftime('%m/%d %H:%M:%S')

        if self.task_name:
            task_name = Colors.format_bold("<%s>" % self.task_name)
            return '%s %s %s' % (_format_title(record.levelno, dt_str), task_name, Colors.format_white(record.msg))
        else:
            return '%s %s' % (_format_title(record.levelno, dt_str), Colors.format_white(record.msg))

class ObsidianFormatter(Formatter):
    def __init__(self, task_name=None):
        self.task_name = task_name

        super(ObsidianFormatter, self).__init__()

    def format(self, record):

        def _format_title(levelno, dt_str):
            map = {
                logging.DEBUG: "[D %s]" % dt_str,
                logging.INFO: "[I %s]" % dt_str,
                logging.WARN: "[W %s]" % dt_str,
                logging.ERROR: "[E %s]" % dt_str,
                logging.CRITICAL: "[C %s]" % dt_str
            }
            return map[levelno]

        dt_str = datetime.datetime.now().strftime('%m/%d %H:%M:%S')

        if self.task_name:
            task_name = "<%s>" % self.task_name
            return '%s %s %s' % (_format_title(record.levelno, dt_str), task_name, record.msg)
        else:
            return '%s %s' % (_format_title(record.levelno, dt_str), record.msg)

class Logger(logging.Logger):

    def __init__(self, name, debug=True):
        logging.Logger.__init__(self, name)
        self._debug  = debug
        self.name    = name
        self.handler = None

        self.propagate = False

        self.set_debug(debug)

    def set_debug(self, debug):
        if debug == True:
            self.setLevel(logging.DEBUG)
            s_formatter = ObsidianDebugFormatter(self.name)
        else:
            self.setLevel(logging.INFO)
            s_formatter = ObsidianFormatter(self.name)

        if self.handler != None:
            self.removeHandler(self.handler)

        # add handler , just shows log via stderr
        self.handler = logging.StreamHandler(sys.stdout)
        self.handler.setFormatter(s_formatter)

        self.addHandler(self.handler)
