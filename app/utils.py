#coding=utf-8
__author__ = 'Nigshoxiz'

import time
import datetime
import re, os
import json
import calendar
import hashlib
from app.error_code import errcode

# password hash salt
salt = b"\x87\x93\xfb\x00\xfa\xc2\x88\xba$\x86\x98\'\xba\xa8\xc6"

# consts
class PRIVILEGES:
    ULTIMATE = 0
    ROOT_USER = 1
    FREE_USER = 2
    INST_OWNER = 4
    EVERYONE = 8

class WS_TAG:
    MPW = "MPW"
    CLIENT = "CLIENT"
    CLIENT_CONTROL = "CLIENT_CONTROL"
    CLIENT_BYE = "CLIENT_BYE"
    APP = "APP"
    FTM = "FTM"

def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

def get_file_hash(filename):
    file = open(filename , 'rb')
    data = file.read(1024)
    return hashlib.md5(data).hexdigest()


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
#print("\nfinal line number: %s" % (
#    get_line_number(get_file_directory())
#    + get_line_number(get_file_directory()+"/../ftp_manager")
#    + get_line_number(get_file_directory()+"/../process_watcher")
#    + get_line_number(get_file_directory()+"/../websocket_server")
#    ))

# test f**king dateUtil
#print(timeUtil.getReadableTime(timeUtil.getCurrentUTCtimestamp(),8))
#print(timeUtil.getUTCtimestamp("2016-6-23 00:25",0))