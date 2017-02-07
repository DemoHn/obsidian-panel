#coding=utf-8
__author__ = 'Nigshoxiz'

import time
import datetime
import re, os
import json
from random import randint
import hashlib, traceback
import yaml
from app.error_code import errcode

# password hash salt
salt = b"\x87\x93\xfb\x00\xfa\xc2\x88\xba$\x86\x98\'\xba\xa8\xc6"

from ob_logger import Logger
_logger = Logger("_utils", debug=False)

# consts
class PRIVILEGES:
    ULTIMATE = 0
    ROOT_USER = 1
    FREE_USER = 2
    INST_OWNER = 4
    EVERYONE = 8

def get_file_directory():
    full_path = os.path.realpath(__file__)
    path,file = os.path.split(full_path)
    return path

def get_file_hash(filename):
    file = open(filename , 'rb')
    data = file.read(1024)
    return hashlib.md5(data).hexdigest()

def generate_random_string(bits):
    _str = ""
    for i in range(0,bits):
        _str += chr(randint(0,25) + 65)
    return _str

# read VERSION
def get_version():
    f = open("VERSION", "r")
    version = f.read()
    return version.strip()

# debug mode
def is_debug():
    DEBUG_LOCK = "debug.lock"
    if os.path.exists(DEBUG_LOCK):
        return True
    else:
        return False

# read config.yaml
def read_config_yaml():

    def _merge_dict(dict_data, dict_tmpl):
        for item in dict_tmpl:
            if dict_data.get(item) == None:
                dict_data[item] = dict_tmpl[item]
            elif type(dict_tmpl[item]) == dict:
                if type(dict_data[item]) != dict:
                    # e.g. : A['a'] = 1, B['a'] = {'c' : 'b'}
                    # then -> A['a'] = {'c' : 'b'}
                    dict_data[item] = dict_tmpl[item]
                else:
                    _merge_dict(dict_data[item], dict_tmpl[item])

        return dict_data

    config_yaml = "config.yaml"
    config_yaml_sample = "config.yaml.sample"

    fsr_docs = None
    fr_docs  = None
    try:
        fsr = open(config_yaml_sample, "r")
        fsr_docs = yaml.load(fsr)
        fsr.close()
    except:
        _logger.error(traceback.format_exc())
        fsr.close()
        return None

    if os.path.exists(config_yaml):
        try:
            fr = open(config_yaml, "r")
            fr_docs = yaml.load(fr)
            fr.close()
        except:
            _logger.error(traceback.format_exc())
            fr.close()
            return None
    else:
        fr_docs = {}

    # update config.yaml if config.yaml.sample has some new keys
    fr_docs = _merge_dict(fr_docs, fsr_docs)
    merged_config_text = yaml.dump(fr_docs, default_flow_style=False)

    try:
        f = open(config_yaml, "w+")
        f.write(merged_config_text)
        f.close()
    except:
        f.close()
        return None

    return fr_docs

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
