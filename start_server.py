import logging

import os
from app import app as _app
from app import logger
from app.controller.global_config import GlobalConfig
from app.controller.init_main_db import init_database
from ob_logger import Logger
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

# init directories
init_directory()
init_database(logger=logger)

if __name__ == "__main__":
    _app.run(debug=True)
