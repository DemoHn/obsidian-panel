from app import db
import datetime
import hashlib
import re
from app.utils import salt

# password salt
SALT = salt

class Users(db.Model):
    __tablename__ = "ob_user"
    id = db.Column(db.Integer, primary_key= True, unique=True, autoincrement=True)
    """ob_token
    username
    """
    username = db.Column(db.String(80), unique=True)

    """
    User password (hashed of course.)
    """
    hash = db.Column(db.String(120))

    """
    User's email address (optional)

    """
    email = db.Column(db.String(120))
    """
    User join time
    """
    join_time = db.Column(db.DateTime)

    """
    :privilege: defines the user's authorization group.
    """
    privilege = db.Column(db.Integer , default=0)

    token_relation = db.relationship("UserToken", lazy='dynamic', backref="ob_user")
    ftp_account_relation = db.relationship("FTPAccount", lazy='dynamic', backref="ob_user")

    def __repr__(self):
        return "<User %s, privilege=%s>" % (self.username, self.privilege)

    def insert(self):
        if len(self.username) > 32:
            raise ValueError("username `%s` is too long!" % self.username)

        password_re = "^\w{6,30}$"
        if re.match(password_re, self.password) == None:
            raise ValueError("password format doesn't matches!")

        self.hash = hashlib.md5(self._password.encode('utf-8') + SALT).hexdigest()
        self.join_time = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

        return True

    def insert_byhash(self):
        self.join_time = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def compare_password(username, password, uid = None):
        '''

        :param username: input username
        :param password: input password
        :return: (<password fits>, <query result>)
        '''
        hash = hashlib.md5(password.encode('utf-8') + SALT).hexdigest()

        if uid != None:
            record = db.session.query(Users).filter(Users.id==uid, Users.hash==hash).first()
        else:
            record = db.session.query(Users).filter(Users.username==username, Users.hash==hash).first()

        if record == None:
            return (False, None)
        else:
            return (True, record)

    @staticmethod
    def set_password(password, uid = None, username = None):
        password_re = "^\w{6,30}$"
        if re.match(password_re, password) == None:
            raise ValueError("password format doesn't matches!")

        _hash = hashlib.md5(password.encode('utf-8') + SALT).hexdigest()

        rec = None
        if uid == None:
            if username == None:
                raise ValueError("null username or uid!")
            else:
                rec = db.session.query(Users).filter(Users.username == username).first()
        else:
            rec = db.session.query(Users).filter(Users.id == uid).first()

        if rec != None:
            rec.hash = _hash
            db.session.commit()
        else:
            raise ValueError("uid or username not find!")

    @staticmethod
    def search_username(username):
        rec = db.session.query(Users).filter(Users.username == username).first()

        if rec == None:
            return False
        else:
            return True