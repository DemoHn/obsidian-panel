from task_scheduler import logger, register_task
from datetime import datetime

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

@register_task("* * * * * 0 0 0")
def daily_log(*args, **kwargs):
    logger.info("Today is %s" % datetime.now().strftime("%Y-%m-%d"))
    logger.info("If you see this log, that means task_scheduler works correctly.")
