__author__ = "Nigshoxiz"

from app import db

class TaskLog(db.Model):
    __tablename__ = "ob_task_log"

    # log id
    log_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    # task id
    task_id = db.Column(db.Integer, db.ForeignKey("ob_background_task.task_id"))

    # issue time
    issue_time = db.Column(db.DateTime)

    # issue result
    issue_result = db.Column(db.Boolean)

    # cost duration
    duration = db.Column(db.Float)
