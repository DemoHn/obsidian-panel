__author__ = "Nigshoxiz"

from app import db

class JavaBinary(db.Model):
    __tablename__ = "ob_java_bin"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # java version (main)
    major_version = db.Column(db.String(100))
    # minor version. e.g. : '1.8.10_92'. '1.8.10' is major and '_92' is minor
    minor_version = db.Column(db.String(20))
    # java dir
    bin_directory = db.Column(db.Text)
    # install time
    install_time  = db.Column(db.DateTime)

    bin_relation = db.relationship("ServerInstance", lazy='dynamic', backref="ob_java_bin")

    def __repr__(self):
        return "<id=%s, version=%s_%s, dir=%s>" % (self.id,
                                                   self.major_version,
                                                   self.minor_version,
                                                   self.bin_directory)