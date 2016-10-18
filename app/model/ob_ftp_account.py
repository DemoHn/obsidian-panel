from app import db

class FTPAccount(db.Model):
    __tablename__ = "ob_ftp_account"

    # account id
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    # username for this ftp account (different from login account!)
    username = db.Column(db.String(80), unique=True)

    # hash
    hash = db.Column(db.String(120))

    # working dir
    working_dir = db.Column(db.Text)

    # last login
    last_login = db.Column(db.DateTime)

    # owner's uid
    owner_id = db.Column(db.Integer, db.ForeignKey("ob_user.id"))

    #permission str
    permission = db.Column(db.String(50), default="elradfmw")

    def __repr__(self):
        return "<owner_id = %s, cwd = %s, username = %s>" % \
               (self.owner_id, self.working_dir, self.username)