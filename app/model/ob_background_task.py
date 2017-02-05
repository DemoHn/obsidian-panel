__author__ = "Nigshoxiz"

from app import db

class BackgroundTask(db.Model):
    __tablename__ = "ob_background_task"

    task_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    # task name (the only way to identify task, be careful!)
    task_name = db.Column(db.String(80))

    #task args (string separated by comma)
    task_args = db.Column(db.Text)

    #owner id
    owner_id = db.Column(db.Integer, db.ForeignKey("ob_user.id"))

    # crontab string
    # **NOTICE**: The following defined format is differnet from the crontab format normally we use!
    #
    # format:
    # <year> <month_of_the_year> <day_of_the_month> <week> <day_of_the_week> <hour> <minute> <second>
    #
    # example:
    # * * * * Fri */6 30 0
    # means Every year/month/day/day_of_week, every Friday, per 6 hour (i.e. : 6am, 12am, 6pm, 12pm), minute = 30, second = 0
    # Thus the task will be executed 4 times per day: 6:30am, 12:30am, 6:30pm, 12:30pm

    cron_data = db.Column(db.String(80))

    # create time
    create_time = db.Column(db.DateTime)
