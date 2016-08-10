__author__ = "Nigshoxiz"

from app import db
from datetime import datetime

from .ob_user import Users

class UserToken(db.Model):
    __tablename__ = "ob_token"
    token_id = db.Column(db.Integer, primary_key=True,autoincrement=True)

    # user id
    uid =  db.Column(db.Integer, db.ForeignKey("ob_user.id"))

    token = db.Column(db.String(50))
    #last login Time
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return "<username %s, token=%s>" % (self.username, self.token)

    def insert(self, username):
        self.last_login = datetime.now()
        l = Users.query.filter_by(username=username).first()
        self.uid = l.id

        db.session.add(self)
        db.session.commit()
