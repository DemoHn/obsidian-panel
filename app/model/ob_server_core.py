__author__ = "Nigshoxiz"

from app import db
from datetime import datetime

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
    create_time = db.Column(db.DateTime)
    """
    file's md5 hash
    """
    file_hash = db.Column(db.String(80))

    """
    mod's name. Like Kcaultron, Bukkit, etc.
    """
    mod_name = db.Column(db.String(100))
    mod_version = db.Column(db.String(10))
    minecraft_version = db.Column(db.String(10))

    def __repr__(self):
        pass

    def create(self):
        # TODO
        pass