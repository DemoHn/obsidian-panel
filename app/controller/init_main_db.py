__author__ = "Nigshoxiz"
from app.controller.global_config import GlobalConfig
from app.controller.config_env import DatabaseEnv
from sqlalchemy_utils import create_database, database_exists
from app import app, db

from app.model.ob_user import Users

def init_database(logger=None):

    gc = GlobalConfig.getInstance()
    db_env = DatabaseEnv()

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
    gc = GlobalConfig.getInstance()
    _username = gc.get("temp_superadmin_username")
    _email    = gc.get("temp_superadmin_email")
    _hash     = gc.get("temp_superadmin_hash")


    #for superadmin, privilege = 1
    try:
        super_admin_user = Users(_username,1, email=_email, hash= _hash)
        db.session.add(super_admin_user)
        db.session.commit()

        # if everything works correctly <including the inserting operation above>,
        # it is time to delete account data
        gc.delete("temp_superadmin_username")
        gc.delete("temp_superadmin_email")
        gc.delete("temp_superadmin_hash")

        return True
    except:
        return False
