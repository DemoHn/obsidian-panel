__author__ = "Nigshoxiz"
from app.controller.global_config import GlobalConfig
from app.controller.config_env import DatabaseEnv
from sqlalchemy_utils import create_database, database_exists
from app import app, db
from app.model import Users, UserToken, JavaBinary

from datetime import datetime
from ob_logger import Logger
import traceback
import json

g_logger = Logger("StartUp", debug=True)
from app.utils import PRIVILEGES
def init_database(logger=None):

    gc = GlobalConfig.getInstance()
    db_env = DatabaseEnv()

    if logger == None:
        logger = g_logger

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

        gc.set("database_uri", database_uri)
        # let SQLAlchemy know the database URI
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

        if not database_exists(database_uri):
            create_database(database_uri)

        db.create_all(app=app)
        db.session.commit()
    else:
        logger.warning("Main database NOT initialized as starter configuration not finished yet.")

def init_db_data(root_user):
    if root_user == None:
        return None
    else:
        u = Users(
            username = root_user.get("username"),
            email = root_user.get("email"),
            privilege = PRIVILEGES.ROOT_USER
        )
        u._password = root_user.get("password")
        try:
            u.insert()
        except:
            print(traceback.format_exc())
            return False
        return True
    pass

# [deprecated]
def migrate_superadmin():
    '''
    This function aims to migrate superadmin's account data (including username, email
    , password hash) from temporal SQLite database to main database.

    Why exists? At the beginning, database setting has not been configured yet. Thus it's
    impossible to store superadmin's account data to user's database directly.

    How it works? read superadmin's account data from GlobalConfig database (in which the data is stored
    when step 1 is done.) and run init_database() to ensure SQLAlchemy API is available. Next,
    just use the API to insert data and delete the original one since there's no reason to keep it then.

    :return:
    '''
    if app.config.get("SQLALCHEMY_DATABASE_URI") == None:
        # ensure main database is initialized and SQLAlchemy available.
        init_database()

    # read data from GlobalConfig database
    gc = GlobalConfig()
    _username = gc.get("temp_superadmin_username")
    _email    = gc.get("temp_superadmin_email")
    _hash     = gc.get("temp_superadmin_hash")

    _java_bin_arr = gc.get("temp_java_binary")

    #for superadmin, privilege = 1
    try:
        super_admin_user = Users(username=_username, privilege = PRIVILEGES.ROOT_USER, email=_email, hash= _hash)
        try:
            super_admin_user.insert_byhash()
        except:
            traceback.print_exc()
        # if everything works correctly <including the inserting operation above>,
        # it is time to delete account data
        gc.set("temp_superadmin_username", "")
        gc.set("temp_superadmin_email", "")
        gc.set("temp_superadmin_hash", "")

        g_logger.debug(_java_bin_arr)

        # for empty value, just emit it
        if _java_bin_arr == None:
            gc.set("temp_java_binary", "")
            return True

        if _java_bin_arr == "":
            return True

        for java_binary in json.loads(_java_bin_arr):
            j = JavaBinary(
                major_version = java_binary.get("major_version"),
                minor_version = java_binary.get("minor_version"),
                bin_directory = java_binary.get("bin_directory"),
                install_time  = datetime.fromtimestamp(java_binary.get("install_time"))
            )
            db.session.add(j)
        db.session.commit()
        gc.set("temp_java_binary", "")
        return True
    except:
        g_logger.error(traceback.format_exc())
        return False
