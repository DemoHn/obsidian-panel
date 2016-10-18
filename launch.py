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
    from start_server import _app

    from chaussette.backend import _backends
    from chaussette.backend._eventlet import Server as eventlet_server

    from chaussette import logger
    from chaussette.server import make_server

    _host = "fd://%d" % int(sys.argv[4])
    def _make_server():
        try:
            # instill eventlet_server instance to `_backends` dict to bypass the restriction!
            _backends['eventlet'] = eventlet_server
            httpd = make_server(_app, host=_host,
                                backend='eventlet')

            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)

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
    from ftp_manager import FTPManager
    __author__ = "Nigshoxiz"
    # import app
    # m = FTPManager(2121)
    # m.launch()
    # First .py module
    manager = FTPManager(2121)
    manager.launch()

def start_websocket_server():
    from websocket_server import start_websocket_server
    start_websocket_server()

def start_process_watcher():
    from process_watcher.watchdog import Watchdog
    from process_watcher.inst_events import InstanceEventEmitter
    from process_watcher.mq_proxy import MessageQueueProxy

    watcher = Watchdog.getWDInstance()
    watcher.launch(hook_class=InstanceEventEmitter)

    proxy = MessageQueueProxy()
    proxy.listen()

launch_branch_name = sys.argv[2]

if launch_branch_name == "app":
    start_chaussette(False)
elif launch_branch_name == "ftp_manager":
    start_ftp_manager()
elif launch_branch_name == "process_watcher":
    start_process_watcher()
elif launch_branch_name == "websocket_server":
    start_websocket_server()
