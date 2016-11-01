__author__ = "Nigshoxiz"

from app import db

class BackgroundTask(db.Model):
    __tablename__ = "ob_background_task"

    # id
    task_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    # task type (registered on other functions)
    task_type = db.Column(db.String(80))

    #task args (string separated by comma)
    task_args = db.Column(db.Text)

    #owner id
    owner_id = db.Column(db.Integer, db.ForeignKey("ob_user.id"))

    # interval number or crontab string (for interval number, the unit is second)
    cron_data = db.Column(db.String(80))

    # create time
    create_time = db.Column(db.DateTime)


