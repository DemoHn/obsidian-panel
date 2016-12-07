__author__ = "Nigshoxiz"

'''
[circus]
endpoint = tcp://127.0.0.1:5555
pubsub_endpoint = tcp://127.0.0.1:5556
stats_endpoint = tcp://127.0.0.1:5557

[watcher:web]
copy_env = True
virtualenv = ./env
working_dir = ./

use_sockets = True
cmd = ./env/bin/chaussette run.app
args = --fd $(circus.sockets.web) --backend eventlet
numprocesses = 5

[socket:web]
host = 0.0.0.0
port = 5000
'''

# Dev Note:
# For some strange reasons, it is not allowed to run a chaussette instance
# using eventlet backend in python3 (chaussette version: v0.13.0, which is the newest version pip could download).
# That is, we can't run `chaussette run.app --backed eventlet` to start server directly.
# In fact, chaussette supports eventlet backend in python3 internally, it just denies `eventlet` as an option
# of `--backend` in command line. Considering the stability of eventlet library in python3, which has been
# improved a lot since the release date of chaussette v0.13.0 (2015), we monkey-patch it to bypass the
# restriction of command line .
#
# And How to run in circus?
#
# Just append the following configuration:
#
# [watcher:xxx]
# cmd = python start_chaussette.py --fd $(circus.sockets.web)
#
# Nigshoxiz
# 2016-8-16

# import app

import sys

def start_chaussette(use_reloader):
    from app import app as _app
    from app import logger
    from app.controller.global_config import GlobalConfig
    from app.controller.init_main_db import init_database

    from chaussette.backend import _backends
    from chaussette.backend._eventlet import Server as eventlet_server
    from chaussette.server import make_server

    import os
    _host = "fd://%d" % int(sys.argv[4])

    logger.debug("This is Main Server (%s)" % os.getpid())
    def init_directory():
        gc = GlobalConfig.getInstance()
        dirs = [
            gc.get("base_dir"),
            gc.get("uploads_dir"),
            gc.get("files_dir"),
            gc.get("servers_dir"),
            gc.get("lib_bin_dir"),
            gc.get("sqlite_dir")
        ]

        for item in dirs:
            if not os.path.isdir(item):
                os.makedirs(item)

    def _make_server():
        try:
            # instill eventlet_server instance to `_backends` dict to bypass the restriction!
            _backends['eventlet'] = eventlet_server
            httpd = make_server(_app, host=_host,
                                backend='eventlet')

            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)

    # init directories
    init_directory()

    # init database
    init_database(logger=logger)

    if use_reloader:
        try:
            from werkzeug.serving import run_with_reloader
        except ImportError:
            logger.info("Reloader requires Werkzeug: "
                        "'pip install werkzeug'")
            sys.exit(0)
        run_with_reloader(_make_server)
    else:
        _make_server()

def start_ftp_manager():
    from ftp_manager import start_FTP_manager
    start_FTP_manager()

def start_websocket_server():
    from websocket_server import start_websocket_server
    start_websocket_server()

def start_process_watcher():
    '''
    from process_watcher.watchdog import Watchdog
    from process_watcher.mq_events import EventSender, WatcherEvents
    from process_watcher.mq_proxy import MessageQueueProxy

    watcher = Watchdog.getWDInstance()
    watcher.launch(hook_class=EventSender)
    # init recv events
    proxy = MessageQueueProxy.getInstance()
    WatcherEvents()
    proxy.listen()
    '''
    from process_watcher import start_process_watcher
    start_process_watcher()

launch_branch_name = sys.argv[2]

if launch_branch_name == "app":
    start_chaussette(False)
elif launch_branch_name == "ftp_manager":
    start_ftp_manager()
elif launch_branch_name == "process_watcher":
    start_process_watcher()
elif launch_branch_name == "websocket_server":
    start_websocket_server()
