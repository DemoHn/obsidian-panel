__author__ = "Nigshoxiz"

from app import db
from datetime import datetime

class ServerInstance(db.Model):
    __tablename__ = "ob_server_instance"

    inst_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # the user who ownes this server instance
    owner_id = db.Column(db.Integer, db.ForeignKey("ob_user.id"))
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

    def __repr__(self):
        return "<id=%s, port=%s, max_RAM=%s>" % (self.inst_id,
                                                 self.listening_port,
                                                 self.max_RAM)


