from app import db

class FTPAccount(db.Model):
    __tablename__ = "ob_ftp_account"

    # account id
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    # inst id
    inst_id = db.Column(db.Integer, db.ForeignKey("ob_server_instance.inst_id"))

    # username for this ftp account (different from login account!)
    username = db.Column(db.String(80), unique=True)

    # hash
    hash = db.Column(db.String(120))

    # last login
    last_login = db.Column(db.DateTime)

    # owner's uid
    owner_id = db.Column(db.Integer, db.ForeignKey("ob_user.id"))

    #permission str
    permission = db.Column(db.String(50), default="elradfmw")

    # default password (if True, than its password will be the as its login password)
    default_password = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<owner_id = %s, inst_id = %s, username = %s>" % \
               (self.owner_id, self.inst_id, self.username)