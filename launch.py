__author__ = "Nigshoxiz"

# Dev Note:
# For some strange reasons, it is not allowed to run a chaussette instance
# using eventlet backend in python3 (chaussette version: v0.13.0, which is the newest version pip could download).
# That is, we can't run `chaussette run.app --backed eventlet` to start server directly.
# In fact, chaussette supports eventlet backend in python3 internally, it just denies `eventlet` as an option
# of `--backend` in command line. Considering the stability of eventlet library in python3, which has been
# improved a lot since the release date of chaussette v0.13.0 (2015), we monkey-patch it to bypass the
# restriction of command line .
#
# And How to config circus?
#
# Just append the following configuration:
#
# [watcher:xxx]
# cmd = python start_chaussette.py --fd $(circus.sockets.web)
#
# Nigshoxiz
# 2016-8-16

import sys, getopt, os

def start_chaussette():
    from app import app as _app
    from app import logger, proxy
    from app.utils import read_config_yaml, is_debug
    from app.mq_events import WebsocketEventHandler
    from app.controller.global_config import GlobalConfig
    from app.controller.init_main_db import init_database

    from chaussette.backend import _backends
    from chaussette.backend._eventlet import Server as eventlet_server
    from chaussette.server import make_server

    _config = read_config_yaml()
    debug = is_debug()

    # variables
    host = _config['server']['host']
    port = int(_config['server']['listen_port'])
    use_reloader = _config['server']['use_reloader']
    circusd_end_port = _config['circus']['end_port']
    redis_port = _config['redis']['listen_port']
    zmq_port   = _config['broker']['listen_port']

    logger.set_debug(debug)
    _app.config["_circusd_end_port"] = circusd_end_port
    _app.config["_zmq_port"] = zmq_port
    _app.config["_debug"] = debug

    logger.info("This is Main Server (%s)" % os.getpid())
    def init_directory():
        gc = GlobalConfig.getInstance()
        dirs = [
            gc.get("base_dir"),
            gc.get("uploads_dir"),
            gc.get("files_dir"),
            gc.get("servers_dir"),
            gc.get("lib_bin_dir"),
            gc.get("sqlite_dir"),
            # it's totally useless to store a directory's name into database
            # why not just name it?
            # 2017-2-7
        ]

        for item in dirs:
            if not os.path.isdir(item):
                os.makedirs(item)

    def init_mq_proxy():
        proxy.register(WebsocketEventHandler)
        proxy.listen(background=True)

    def wrap_socketio_server():
        import socketio
        from websocket_server.ws_conn import WSConnections

        mgr = socketio.RedisManager("redis://localhost:%s/0" % redis_port)
        sio = socketio.Server(client_manager=mgr, async_mode='eventlet')

        #init
        ws = WSConnections.getInstance(sio)
        ws.init_events()
        app = socketio.Middleware(sio, _app)

        return app

    def _make_server():
        try:
            # instill eventlet_server instance to `_backends` dict to bypass the restriction!
            _backends['eventlet'] = eventlet_server

            app = wrap_socketio_server()
            httpd = make_server(app, host=host, port=port, backend='eventlet')

            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)

    # init directories
    init_directory()

    # init message queue proxy
    init_mq_proxy()

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

def start_ftp_manager(**kwargs):
    from ftp_manager import start_FTP_manager
    start_FTP_manager(**kwargs)

def start_zeromq_broker(**kwargs):
    from websocket_server import start_zeromq_broker
    start_zeromq_broker(**kwargs)

def start_process_watcher(**kwargs):
    from process_watcher import start_process_watcher
    start_process_watcher(**kwargs)

def start_task_scheduler(**kwargs):
    from task_scheduler import start_task_scheduler
    start_task_scheduler(**kwargs)

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:")
except getopt.GetoptError as err:
    print(err, file=sys.stderr)
    sys.exit(2)

launch_branch_name = None
# parse args
for o, a in opts:
    if o == "-b":
        launch_branch_name = a

launch_map = {
    "app" : start_chaussette,
    "ftp_manager" : start_ftp_manager,
    "process_watcher" : start_process_watcher,
    "zeromq_broker" : start_zeromq_broker,
    "task_scheduler" : start_task_scheduler
}

if launch_map.get(launch_branch_name) != None:
    func = launch_map.get(launch_branch_name)
    func()
