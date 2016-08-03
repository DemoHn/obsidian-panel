__author__ = "Nigshoxiz"
from app.controller.global_config import GlobalConfig
from app.controller.config_env import DatabaseEnv
from sqlalchemy_utils import create_database, database_exists
from app import app, db

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

        if not database_exists(database_uri):
            create_database(database_uri)

        db.create_all(app=app)
    else:
        logger.warning("Main database NOT initialized as starter configuration not finished yet.")

