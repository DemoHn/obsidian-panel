from app import db
import datetime
import hashlib
import re
from app.utils import salt

# password salt
SALT = salt

class Users(db.Model):
    __tablename__ = "ob_user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    username
    """
    username = db.Column(db.String(80),unique=True)

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
    <del> OBSOLETE:
    There are 2 kinds of users:
    1) Super User (only 1), Owns all privileges and can control all instances. [privilege=0]
    2) Ordinary Admin User. Owns all privileges in self-created instance. [privilege=1]
    </del>
    """
    privilege = db.Column(db.Integer , default=0)

    def __init__(self, username, privilege, email=None, hash = None, password = None):
        self.username   = username
        self._password  = password
        self.privilege  = privilege
        self.email = email
        self.hash = hash

    def __repr__(self):
        return "<User %s, priv=%s>" % (self.username, self.privilege)

    def insert(self):
        if len(self.username) > 32:
            raise ValueError("username `%s` is too long!" % self.username)

        password_re = "^\w{6,30}$"
        if re.match(password_re,self._password) == None:
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
    def compare_password(username, password):
        hash = hashlib.md5(password.encode('utf-8') + SALT).hexdigest()

        record = Users.query.filter_by(username=username, hash = hash).first()

        if record == None:
            return False
        else:
            return True

    @staticmethod
    def search_username(username):
        rec = Users.query.filter_by(username=username).first()

        if rec == None:
            return False
        else:
            return True

