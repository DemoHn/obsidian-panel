#coding=utf-8
__author__ = 'Nigshoxiz'

import time
import datetime
import re, os
import json
import calendar
from app.error_code import errcode

# password hash salt
salt = b"\x87\x93\xfb\x00\xfa\xc2\x88\xba$\x86\x98\'\xba\xa8\xc6"
def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

class timeUtil:
    def __init__(self):
        pass

    @staticmethod
    def getCurrentUTCtimestamp():
        # get timestamp
        # time.timezone represents for the seconds that current timestamp delayed
        return int(datetime.datetime.now().timestamp())

    @staticmethod
    def getReadableTime(utc_timestamp,timezone):
        # final string e.g: 2015-10-12 17:39
        local_timestamp = int(utc_timestamp) + int(timezone)*3600
        return datetime.datetime.utcfromtimestamp(local_timestamp).strftime("%Y-%m-%d %H:%M:%S")

    # def getUTCtimestamp():
    # INPUT :
    @staticmethod
    def getUTCtimestamp(readable_time,timezone):
        # here, timezone means hours before UTC
        # e.g: CST <--> +8
        re_str = "([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+)"
        m = re.search(re_str,readable_time)

        if m == None:
            return False
        else:
            year   = m.group(1)
            month  = m.group(2)
            date   = m.group(3)
            hour   = m.group(4)
            minute = m.group(5)

            # first, we assume that the input datestring is a UTC datetime
            dm     = datetime.datetime(int(year),int(month),int(date),int(hour),int(minute))
            tm     = calendar.timegm(dm.timetuple())
            return int(tm) - timezone * 3600

class dateUtil:

    # get current LOCAL time
    @staticmethod
    def now():
        return datetime.datetime.now()

    @staticmethod
    def getTimestamp(year,month,day):
        n_dm     = datetime.datetime(int(year),int(month),int(day),0,0,0)
        tm     = calendar.timegm(n_dm.timetuple())
        return int(tm)

    @staticmethod
    def getCurrentDatetime():
        dm = datetime.datetime.utcnow()
        year  = int(dm.strftime("%Y"))
        month = int(dm.strftime("%m"))
        day   = int(dm.strftime("%d"))
        hour  = int(dm.strftime("%H"))
        minute= int(dm.strftime("%M"))
        second= int(dm.strftime("%S"))

        date = {}
        date["year"] = year
        date["month"] = month
        date["date"] = day
        date["hour"] = hour
        date["minute"] = minute
        date["second"] = second
        return date

    @staticmethod
    def getCurrentTimeRemainRatioOfMonth():
        dm = datetime.datetime.utcnow()
        year  = int(dm.strftime("%Y"))
        month = int(dm.strftime("%m"))

        last_day     = calendar.monthrange(year,month)[1]
        first_day_tp = datetime.datetime(year,month,1,0,0,0)
        last_day_tp  = datetime.datetime(year,month,last_day,23,59,59)

        # calc timestamp
        now_stamp    = float(time.time() + time.timezone) # UTC timestamp
        first_stamp  = float(time.mktime(first_day_tp.timetuple()))
        last_stamp   = float(time.mktime(last_day_tp.timetuple()))

        return (last_stamp - now_stamp) / (last_stamp - first_stamp)

    @staticmethod
    def DatetimeToTimestamp(date_time):
        return int(time.mktime(date_time.timetuple()))

    @staticmethod
    def getDateAfterDays(relative_days):
        rd = int(relative_days)

        dm = datetime.datetime.utcnow()
        year  = int(dm.strftime("%Y"))
        month = int(dm.strftime("%m"))
        day   = int(dm.strftime("%d"))

        n_dm     = datetime.datetime(int(year),int(month),day,0,0,0)
        tm     = time.mktime(n_dm.timetuple())-time.timezone+rd*24*3600

        tms = datetime.datetime.utcfromtimestamp(tm).strftime("%Y-%m-%d %H:%M:%S")

        re_str = "([0-9]+)-([0-9]+)-([0-9]+) ([0-9]+):([0-9]+)"
        m = re.search(re_str,tms)

        return (m.group(1) , m.group(2), m.group(3))

    @staticmethod
    def getDateAfterMonths(relative_months,year=0,month=0,day=0):

        def _is_leap_year(year):
            if year % 4 == 0:
                if year % 100 == 0:
                    if year % 400 == 0:
                        return 1
                    else:
                        return 0
                else:
                    return 1
            else:
                return 0

        months = [0,31,28,31,30,31,30,31,31,30,31,30,31]
        rm = int(relative_months)

        dm = datetime.datetime.utcnow()
        if year == 0:
            year  = int(dm.strftime("%Y"))
        if month == 0:
            month = int(dm.strftime("%m"))
        if day == 0:
            day   = int(dm.strftime("%d"))
        elif day == "last":
            if month == 2:
                day = 28 + _is_leap_year(year)
            else:
                day = months[month]

        year += int(rm / 12)
        rm = rm % 12

        month = month + rm
        if rm + month > 12:
            year += 1
            month -= 12

        days_of_feb = 28 + _is_leap_year(int(year))
        if month != 2 and day > months[month]:
            day = months[month]
        elif month == 2 and day > days_of_feb:
            # last day of Feb
            day = days_of_feb

        return (year,month,day)
        pass

class returnModel:
    def __init__(self,type="json"):
        self.rtn_type = type
        pass

    def success(self,info,code=200,type="json"):
        rtn = {
            "status":"success",
            "code" :code,
            "info" : info
        }

        if self.rtn_type == "string":
            return json.dumps(rtn)
        else:
            return rtn

    def error(self,error_code,info="",type="json"):
        rtn = {
            "status":"error",
            "code" :error_code,
            "info" : ""
        }

        if info != "":
            rtn["info"] = info
        else:
            try:
                rtn["info"] = errcode[str(error_code)]
            except Exception as e:
                rtn["info"] = "unknown error description"

        if self.rtn_type == "string":
            return json.dumps(rtn)
        else:
            return rtn

class testUtil:
    def compare(item,return_info,code=0,info=""):
        pass
        # standard return_info:
        # {
        #    "status" : "success" | "error",
        #    "code" : XXX,
        #    "info" : YYY
        # }

# 统计本目录下所有*.py文件加在一起的总行数
def get_line_number(directory):
    num = 0
    # get file list
    file_list = os.listdir(directory)

    for item in file_list:
        _item = item
        item = os.path.normpath(directory+"/"+item)
        # if it is file and it is *.py
        if os.path.isfile(item) and item.find(".py") > 0 and item.find(".pyc") < 0:
            f = open(item,"rb")
            nums = len(f.readlines())
            num += nums
            print("---"+str(_item)+": "+str(nums))
            f.close()
        elif os.path.isdir(item+"/") and item != ".git" and item != "assets" and item != "lib":
            subdir = os.path.normpath(item)

            num += get_line_number(subdir)
    return num
# line number stat
#print("\nfinal line number: "+str(get_line_number(get_file_directory())))

# test f**king dateUtil
#print(timeUtil.getReadableTime(timeUtil.getCurrentUTCtimestamp(),8))
#print(timeUtil.getUTCtimestamp("2016-6-23 00:25",0))