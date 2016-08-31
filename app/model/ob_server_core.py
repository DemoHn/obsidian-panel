__author__ = "Nigshoxiz"

from app import db
import hashlib

class ServerCORE(db.Model):
    """
    A server mod is a singular .jar file that runs Minecraft Server instances.
    Because of the low performance and high RAM consumption of MC Vanilla Server (official),
    there're many optimized branches of this mod, like Bukkit, Spigot, KCauldron, SpongeForge and so on.

    Notice: Each mod has its own version number and correspond Minecraft version.
    
    """
    __tablename__ = "ob_server_core"
    core_id = db.Column(db.Integer, primary_key=True)
    file_size = db.Column(db.Integer)
    file_name = db.Column(db.String(100))
    file_dir  = db.Column(db.Text)
    '''
    which user upload this core file.
    '''
    file_uploader = db.Column(db.Integer, db.ForeignKey("ob_user.id"))

    create_time = db.Column(db.DateTime)
    """
    file's md5 hash
    """
    file_hash = db.Column(db.String(80))

    """
    Type of core file. Like Kcaultron, Bukkit, etc.
    """
    core_type = db.Column(db.String(100))
    core_version = db.Column(db.String(10))
    minecraft_version = db.Column(db.String(10), nullable=False)
    note = db.Column(db.Text)

    def __repr__(self):
        return "<core_id = %s, file_name = %s, mc_version = %s>" % \
        (self.core_id, self.file_name, self.minecraft_version)
        pass