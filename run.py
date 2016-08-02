#!flask/bin/python
import os
import logging
from app import app, db
from sqlalchemy_utils import create_database,database_exists

# init database
config = app.config

def init_database(config):
    #database_uri = config
    config = app.config
    db_type = config["DATABASE_TYPE"]

    if db_type == "sqlite":
        database_uri = "sqlite:///%s/%s.db" % (config["SQLITE_DIR"], config["DATABASE_NAME"])
    # elif db_type == "mysql":
    else:
        database_uri = "mysql+pymysql://%s:%s@%s/%s" % (
            config["MYSQL_USERNAME"],
            config["MYSQL_PASSWORD"],
            config["MYSQL_CONNECT_IP"],
            config["DATABASE_NAME"]
        )

    # let SQLAlchemy know the database URI
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    if not database_exists(database_uri):
        create_database(database_uri)

    db.create_all(app=app)

def init_directory(config):
    dirs = [
        config["BASE_DIR"],
        config["UPLOADS_DIR"],
        config["DOWNLOADS_DIR"],
        config["SERVERS_DIR"],
        config["LIB_BIN_DIR"]
    ]

    for item in dirs:
        if not os.path.isdir(item):
            os.makedirs(item)

    if config["DATABASE_TYPE"] == "sqlite":
        if not os.path.isdir(config["SQLITE_DIR"]):
            os.makedirs(config["SQLITE_DIR"])

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

# init directories
init_directory(config)
init_database(config)
init_logger(debug=True)

app.run(debug=True)
