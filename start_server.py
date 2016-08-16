import os
import logging

from app.controller.global_config import GlobalConfig
from app.controller.init_main_db import init_database
from app import socketio
from app import app as _app
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

def init_logger(debug=False):
    logger = logging.getLogger("ob_panel")

    if debug == True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # add handler , just shows log via stderr
    s_handler = logging.StreamHandler()
    s_formatter = logging.Formatter('%(asctime)-15s [%(levelname)s] %(message)s',
                                    datefmt="%Y-%m-%d %H:%M:%S")

    s_handler.setFormatter(s_formatter)
    logger.addHandler(s_handler)
    return logger

logger = init_logger(debug=True)
# init directories
init_directory()
init_database(logger=logger)

if __name__ == "__main__":
    socketio.run(_app,debug=True)
    #app.run(debug=True)
