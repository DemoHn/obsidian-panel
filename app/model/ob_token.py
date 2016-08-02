__author__ = "Nigshoxiz"

from app import db
import datetime
class UserToken(db.Model):
    __tablename__ = "ob_token"
    token_id = db.Column(db.Integer, primary_key=True,autoincrement=True)

    """
    Username
    """
    username = db.Column(db.String(80))

    token = db.Column(db.String(50))

    """
    last login Time
    """
    last_login = db.Column(db.DateTime,default=datetime.datetime.now())

    def __init__(self, username, token):
        self.username = username
        self.token = token

    def __repr__(self):
        return "<username %s, token=%s>" % (self.username, self.token)
