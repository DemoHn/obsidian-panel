from circus import get_arbiter
from circus.circusd import daemonize
from circus.pidfile import Pidfile

import yaml, sys, os, shutil, traceback
from circus.sockets import CircusSocket

# global variables
debug = False
config = {}
sockets = []

def init_debug_flag():
    if len(sys.argv) >= 2:
        if sys.argv[1] == "debug":
            return True
        else:
            return False
    else:
        return False

def read_from_yaml():
    config_file = os.path.normpath(os.path.join(os.getcwd(), "../", "config.yaml"))
    config_sample_file = os.path.normpath(os.path.join(os.getcwd(), "../", "config.yaml.sample"))

    if not os.path.exists(config_file):
        # copy config.sample to config
        shutil.copy(config_sample_file, config_file)

    try:
        fr = open(config_file, "r")
        r = fr.read()
        if len(r) == 0:
            shutil.copy(config_sample_file, config_file)
            r = fr.read()
        config = yaml.load(r)
        return config
    except:
        traceback.print_exc()
        fr.close()
        return None

def write_pid(pid_file):
    pidfile = Pidfile(pid_file)

    try:
        pidfile.create(os.getpid())
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

def load_sockets(socket_config):
    return CircusSocket.load_from_config(socket_config)

debug = init_debug_flag()
config = read_from_yaml()

# logger
if debug:
    logger_class = None
else:
    logger_class = {
        "filename" : config["global"]["log_file"]
    }

### watchers & sockets ###
ENV_DIR = os.path.normpath(os.path.join(os.getcwd(), "../", "env"))
ROOT_DIR = os.path.normpath(os.path.join(os.getcwd(), ".."))

AppWatcher = {
    "copy_env" : True,
    "virtualenv" : ENV_DIR,
    "working_dir" : ROOT_DIR,
    "autostart" : True,
    "use_sockets" : True,
    "priority": 9,
    "stdout_stream": logger_class,
    "cmd" : "python launch.py -b app --host=%s --port=%s --debug=%s --use_reloader=%s --circusd-endport=%s --redis_port=%s --zmq_port=%s" % (
        config["server"]["host"],
        config["server"]["listen_port"],
        debug,
        config["server"]["use_reloader"],
        config["circus"]["end_port"],
        config["redis"]["listen_port"],
        config["broker"]["listen_port"]
    )
}

RedisWatcher = {
    "numprocesses" : 1,
    "autostart" : True,
    "priority": 11,
    "cmd" : "redis-server --port %s" % config["redis"]["listen_port"]
}

ZeroMQBrokerWatcher = {
    "copy_env" : True,
    "virtualenv" : ENV_DIR,
    "working_dir" : ROOT_DIR,
    "numprocesses" : 1,
    "priority" : 10,
    "autostart" : True,
    "stdout_stream": logger_class,
    "cmd" : "python launch.py -b zeromq_broker -p %s --debug=%s" % (
        config["broker"]["listen_port"],
        debug
    )
}

FTPManagerWatcher = {
    "copy_env" : True,
    "virtualenv" : ENV_DIR,
    "working_dir" : ROOT_DIR,
    "numprocesses" : 1,
    "priority" : 8,
    "autostart" : True,
    "stdout_stream": logger_class,
    "cmd" : "python launch.py -b ftp_manager -p %s --debug=%s --zmq_port=%s" % (
        config["ftp"]["listen_port"],
        debug,
        config["broker"]["listen_port"]
    )
}

ProcessWatcher = {
    "copy_env" : True,
    "virtualenv" : ENV_DIR,
    "working_dir" : ROOT_DIR,
    "numprocesses" : 1,
    "priority" : 7,
    "autostart" : True,
    "stdout_stream": logger_class,
    "cmd" : "python launch.py -b process_watcher --debug=%s --zmq_port=%s" % (
        debug,
        config["broker"]["listen_port"]
    )
}

TaskSchedulerWatcher = {
    "copy_env" : True,
    "virtualenv" : ENV_DIR,
    "working_dir" : ROOT_DIR,
    "numprocesses" : 1,
    "priority" : 6,
    "autostart" : True,
    "stdout_stream": logger_class,
    "cmd" : "python launch.py -b task_scheduler --debug=%s --zmq_port=%s" % (
        debug,
        config["broker"]["listen_port"]
    )
}

endpoint = "tcp://127.0.0.1:%s" % config["circus"]["end_port"]
arbiter = get_arbiter(
    [
        AppWatcher,
        RedisWatcher,
        ZeroMQBrokerWatcher,
        TaskSchedulerWatcher,
        FTPManagerWatcher,
        ProcessWatcher
    ],
    controller = endpoint,
    background = True
)

# create pid file
#write_pid('/var/run/ob-panel.pid')
try:
    arbiter.start()
except Exception as e:
    raise(e)
    arbiter.stop()
