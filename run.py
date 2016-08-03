#!flask/bin/python
import os
import logging
from app import app, db
from sqlalchemy_utils import create_database,database_exists

# init database
from app.controller.global_config import GlobalConfig
from app.controller.config_env import DatabaseEnv
import logging

def init_database(logger=None):
    gc = GlobalConfig.getInstance()
    db_env = DatabaseEnv()

    #database_uri = config
    config = app.config
    db_type = db_env.getDatabaseType()

    if gc.get("init_super_admin") == True:
        if db_type == "sqlite":
            database_uri = "sqlite:///%s/%s.db" % (db_env.get("sqlite_dir"),
                                                   db_env.get("db_name"))
        # elif db_type == "mysql":
        else:
            database_uri = "mysql+pymysql://%s:%s@%s/%s" % (
                db_env.get("db_mysql_username"),
                db_env.get("db_mysql_password"),
                db_env.get("db_mysql_ip"),
                db_env.get("db_name")
            )

        # let SQLAlchemy know the database URI
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        app.config["SQLALCHEMY_ECHO"] = False

        if not database_exists(database_uri):
            create_database(database_uri)

        db.create_all(app=app)
    else:
        logger.warning("Main database NOT initialized as starter configuration not finished yet.")


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

app.run(debug=True)
