import os, platform, getopt, sys, subprocess
from string import Template

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:", ["pidfile=", "daemon", "logfile="])
except getopt.GetoptError as err:
    print(err, file=sys.stderr)
    sys.exit(1)

if platform.system() == "Linux":

    logfile = "/var/log/ob-panel.log"
    pidfile = ""
    daemon = ""

    # read opts
    for o, a in opts:
        if o == "--pidfile":
            pidfile = "--pidfile %s" % a
        elif o == "--daemon":
            daemon  = "--daemon"
        elif o == "--logfile":
            logfile = a

    FILE_PATH = os.path.dirname(os.path.realpath(__file__))
    ENV_DIR = os.path.normpath(os.path.join(FILE_PATH, "../", "env"))
    ROOT_DIR = os.path.normpath(os.path.join(FILE_PATH, ".."))

    circusd_ini = '''
[circus]
endpoint = ipc:///tmp/circus.sock
pubsub_endpoint = ipc:///tmp/circus_pubsub.sock
'''
    watchers = ['redis', 'app' , 'ftp_manager', 'process_watcher', 'zeromq_broker', 'task_scheduler']

    tmpl = Template('''
[watcher:$watcher]
cmd = python launch.py -b $watcher
copy_env = True
virtualenv = $env_dir
working_dir = $root_dir
numprocesses = 1
priority = $priority
autostart = True
''')

    _index = len(watchers)
    for watcher in watchers:
        conf = tmpl.substitute(
            watcher = watcher,
            env_dir = ENV_DIR,
            root_dir = ROOT_DIR,
            priority = _index
        )

        _index -= 1

        # debug mode?
        if not os.path.exists(os.path.join(FILE_PATH, "..", "debug.lock")):
            conf +='''
stdout_stream.class = FileStream
stdout_stream.filename = %s
''' % logfile
        circusd_ini += conf

    # write config file
    ini_file = os.path.join(FILE_PATH, ".obsidian_panel.ini")

    f = open(ini_file, 'w+')
    f.write(circusd_ini)
    f.close()

    p = os.system("circusd %s %s %s" % (pidfile, ini_file, daemon))
