import os, platform
from string import Template

if platform.system() == "Linux":

    ENV_DIR = os.path.normpath(os.path.join(os.getcwd(), "../", "env"))
    ROOT_DIR = os.path.normpath(os.path.join(os.getcwd(), ".."))

    circusd_ini = ""
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

        # not in debug mode
        if not os.path.exists("../debug.lock"):
            conf +='''
stdout_stream.class = FileStream
stdout_stream.filename = /var/log/ob-panel.log
'''
        circusd_ini += conf

    # write config file
    f = open(".obsidian_panel.ini", 'w+')
    f.write(circusd_ini)
    f.close()

    os.system("circusd .obsidian_panel.ini")
