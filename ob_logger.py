import logging, datetime, json, sys
from logging import Formatter
# ref : http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
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

class ObsidianFormatter(Formatter):
    def __init__(self, task_name=None):
        self.task_name = task_name

        super(ObsidianFormatter, self).__init__()

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

def Logger(name, debug=True):
    logger = logging.getLogger(name)
    if debug == True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # add handler , just shows log via stderr
    s_handler = logging.StreamHandler(sys.stdout)
    #s_formatter = logging.Formatter(
    #    '[%(levelname)s %(asctime)-15s] <'+name+'> %(message)s',datefmt="%m/%d %H:%M:%S")
    s_formatter = ObsidianFormatter(name)
    s_handler.setFormatter(s_formatter)
    logger.propagate = False
    logger.addHandler(s_handler)
    return logger