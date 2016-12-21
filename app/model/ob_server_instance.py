__author__ = "Nigshoxiz"

from app import db

class ServerInstance(db.Model):
    __tablename__ = "ob_server_instance"

    inst_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # the user who ownes this server instance
    owner_id = db.Column(db.Integer, db.ForeignKey("ob_user.id"))
    # inst_name
    inst_name = db.Column(db.String(100))
    # last time to launch the server
    last_start_time = db.Column(db.DateTime)
    # server core file
    core_file_id = db.Column(db.Integer, db.ForeignKey("ob_server_core.core_id"))
    # java bin file
    java_bin_id  = db.Column(db.Integer, db.ForeignKey("ob_java_bin.id"))
    # :properties:
    # listening port
    listening_port = db.Column(db.Integer, unique=True)
    # max RAM allocated
    max_RAM = db.Column(db.Integer)
    # max user online simultaneously
    max_user = db.Column(db.Integer)
    # instance working directory, which is the root of an instance to start.
    inst_dir = db.Column(db.Text)
    # star (one user could star only one instance)
    # if this instance is starred, it will be shown by default
    star  = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<id=%s, port=%s, max_RAM=%s>" % (self.inst_id,
                                                 self.listening_port,
                                                 self.max_RAM)


