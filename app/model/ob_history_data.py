from app import db

class HistoryData(db.Model):
    __tablename__ = "ob_history_data"

    # data id
    data_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    #date
    time = db.Column(db.DateTime)

    # inst id
    inst_id = db.Column(db.Integer)
    # data key name
    # maybe 'online_player' or 'memory' or something else
    key = db.Column(db.Text)

    # value
    # string data, even the data is a float or int type
    value = db.Column(db.Text)

    def __repr__(self):
        return "<id = %s, time = %s, inst = %s, key = %s, value = %s>" % \
               (self.data_id, self.time.__str__(), self.inst_id, self.key, self.value)

