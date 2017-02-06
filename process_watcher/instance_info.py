from app import db
from app.model import HistoryData
from . import logger

import os, json, traceback
from datetime import datetime
class MCInstanceInfo(object):

    LOG_BLOCK_SIZE = 512
    def __init__(self, total_RAM=None,total_player=None, owner=None, inst_id=None):
        self.total_RAM = total_RAM
        self.RAM     = None
        self.current_player = None
        self.total_player = total_player
        self.owner = owner
        self.inst_id = inst_id

        self.log = []
        # TODO
        self.player_dict = {}
        pass

    def reset(self):
        self.RAM = None
        self.current_player = None

    def _store_log_to_db(self):
        # if inst_id is not set,
        # just ignore the operation
        if self.inst_id == None:
            return

        _index_q = db.session.query(HistoryData).filter(HistoryData.inst_id == self.inst_id and HistoryData.key == "log_index").first()
        # init log index
        if _index_q == None:
            _log_index = HistoryData(
                time = datetime.now(),
                inst_id = self.inst_id,
                key = "log_index",
                value = "0"
            )
            db.session.add(_log_index)
            db.session.commit()

        _len = len(self.log)
        while _len > MCInstanceInfo.LOG_BLOCK_SIZE:
            _index_obj = db.session.query(HistoryData).filter(HistoryData.inst_id == self.inst_id).filter(HistoryData.key == "log_index").first()
            _index = int(_index_obj.value)
            # add log, and pretend it to be an array with json object
            log_str = "["
            for i in range(0, MCInstanceInfo.LOG_BLOCK_SIZE):
                log_str += (json.dumps(self.log[i]) + ",")

            log_str = log_str[:-1]
            log_str += "]"

            # clear first LOG_BLOCK_SIZE number of log
            self.log = self.log[MCInstanceInfo.LOG_BLOCK_SIZE:]
            # update new length of remaining log
            _len = len(self.log)

            # write log_str to db
            _index += 1
            # 1. write index
            _update_dict = {
                "value" : str(_index)
            }
            db.session.query(HistoryData).filter(HistoryData.inst_id == self.inst_id).filter(HistoryData.key == "log_index").update(_update_dict)
            db.session.commit()
            # 2. appened log

            _log_data = HistoryData(
                time = datetime.now(),
                inst_id = self.inst_id,
                key = "log_%s" % _index,
                value = log_str
            )
            db.session.add(_log_data)
            # commit updates
            db.session.commit()

    def _read_log_from_db(self):
        if self.inst_id == None:
            return []

        _index_obj = db.session.query(HistoryData).filter(HistoryData.inst_id == self.inst_id).filter(HistoryData.key == "log_index").first()

        if _index_obj == None:
            return []
        _index = int(_index_obj.value)

        #if len(self.log) < MCInstanceInfo.LOG_BLOCK_SIZE / 4:
        if True:
            _log_obj = db.session.query(HistoryData).filter(HistoryData.inst_id == self.inst_id).filter(HistoryData.key == "log_%s" % _index).first()
            log_val = _log_obj.value
            log_arr = json.loads(log_val)

            return log_arr
        else:
            return []

    def append_log(self, pipe, log_data):
        # pipe = 1 --> 'type' --> 'O'
        # pipe = 2 --> 'type' --> 'E'

        _model = {
            "type" : 'O',
            'log' : log_data
        }
        if pipe == 0:
            _model['type'] = 'I'
        elif pipe == 1:
            _model['type'] = 'O'
        elif pipe == 2:
            _model['type'] = 'E'

        self.log.append(_model)
        # store history log to db
        if len(self.log) > MCInstanceInfo.LOG_BLOCK_SIZE:
            logger.debug("store log")
            self._store_log_to_db()

    def set_RAM(self, RAM):
        self.RAM = RAM

    def set_current_player(self, current_player):
        self.current_player = current_player

    def incr_current_player(self):
        if self.current_player == None:
            self.current_player = 0
        self.current_player += 1

    def decr_current_player(self):
        if self.current_player == None:
            self.current_player = 0
        self.current_player -= 1

    def get_RAM(self):
        return self.RAM

    def get_current_player(self):
        return self.current_player

    def get_owner(self):
        return self.owner

    def get_total_player(self):
        return self.total_player

    def get_total_RAM(self):
        return self.total_RAM

    def get_log(self):
        # if the length of remaining is too short, display the last stored log too.
        try:
            log_arr = self._read_log_from_db()
        except:
            logger.error(traceback.format_exc())
        log_arr += self.log
        return log_arr
