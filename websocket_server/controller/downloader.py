__author__ = "Nigshoxiz"

from websocket_server.server import WSConnections
from app import db

from app.model import JavaBinary
from app.controller.global_config import GlobalConfig
from app.tools.mc_downloader import DownloaderPool, sourceJAVA
from app.tools.mq_proxy import MessageEventHandler, WS_TAG, MessageQueueProxy

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import tarfile
import traceback
import os

class _utils:
    WAIT = 1
    DOWNLOADING = 2
    EXTRACTING = 3
    FINISH = 4
    FAIL = 5
    EXTRACT_FAIL= 6

class DownloadingTasks(object):

    def __init__(self):
        self.tasks = {}
        pass

    def add(self, hash, dw_link):
        _model = {
            "link": dw_link,
            "status": _utils.DOWNLOADING,
            "progress": 0
        }

        self.tasks[hash] = _model

    def delete(self, hash):
        if self.tasks.get(hash) != None:
            del self.tasks[hash]

    def update(self, hash, status = None, progress = None):
        if self.tasks.get(hash) != None:
            _model = self.tasks.get(hash)
            if status != None:
                _model["status"] = status
            if progress != None:
                _model["progress"] = progress

    def get(self, hash):
        if self.tasks.get(hash) != None:
            return self.tasks.get(hash)
        else:
            return None

    def get_all(self):
        return self.tasks

    def has_working_link(self, link):
        for item in self.tasks:
            if self.tasks[item]['link'] == link:
                return True
        return False


class DownloaderEventHandler(MessageEventHandler):

    __prefix__ = "downloader"
    def __init__(self):

        #self.proxy = MessageQueueProxy(WS_TAG.CONTROL)
        self.tasks_pool = DownloadingTasks()
        self.scheduler  = BackgroundScheduler()
        MessageEventHandler.__init__(self)

    def download_newest_java(self, flag, values):
        s = sourceJAVA()
        list = s.get_download_list()
        # most newest one
        newest_version = list[0]
        self.add_download_java_task(flag, newest_version)

    def add_download_java_task(self, flag, values):
        '''
            when accessing this route, a new JDK starts downloading in the background.
            Due to the limitation of current technology, we only allow one file to download at the
            same time.
            request params: [POST]
            :major: <major version of java>
            :minor: <minor version of java>
            '''
        uid, sid, src, dest = self.pool.get(flag)
        gc = GlobalConfig.getInstance()
        def _schedule_get_progress(self, hash):
            # fetch and update data
            dp = DownloaderPool.getInstance()
            _t = dp.get(hash)
            if _t != None:
                inst = _t.dl
                _dw, _filesize = inst.getProgress()
                #print("[progress] %s / %s" % (_dw, _filesize))
                # update data on download_queue
                if _filesize > 0 and \
                                _dw != None and _filesize != None:
                    #    download_queue[hash]["progress"] = _dw / _filesize
                    # _utils.send_dw_signal("_get_progress", hash, (_dw, _filesize))
                    self.tasks_pool.update(hash, progress=_dw / _filesize)
                    _send_dw_signal("_get_progress", hash, (_dw, _filesize))

        def _send_dw_signal(event_name, hash, result):
            ws = WSConnections.getInstance()
            v = {
                "event": event_name,
                "hash": hash,
                "result": result,
                "flag" : flag
            }
            ws.send_data("message", v, uid=uid)

            #event = "%s.%s" % (ControllerOfDownloader.prefix, event_name)
            #self.proxy.send(event, WS_TAG.CLIENT, flag, v)

        def _add_java_task(link, download_dir, binary_dir):
            sch_job = None
            '''
            add task of downloading java, with hooks.
            :return: (<instance>, <download_hash>)
            '''
            def _extract_file(download_result, filename):
                # for abnormal input parameters(like empty filename), the only thing is to terminate
                # next steps!
                if download_result == False or filename == None:
                    return None

                logging.debug("Download Result: %s" % download_result)
                logging.debug("Start Extracting File...")

                # send extract_start event
                self.tasks_pool.update(hash, status=_utils.EXTRACTING)
                #download_queue[hash]["status"] = _utils.EXTRACTING
                _send_dw_signal("_extract_start", hash, True)

                # open archive
                archive = tarfile.open(filename)
                try:
                    archive.extractall(path=root_dir)
                except:
                    archive.close()
                    self.tasks_pool.update(hash, status=_utils.EXTRACT_FAIL)
                    #download_queue[hash]["status"] = _utils.EXTRACT_FAIL
                    # send extract_finish event (when extract failed)
                    _send_dw_signal("_extract_finish", hash, False)
                    return None

                logging.debug("extract dir: %s, finish!" % root_dir)
                archive.close()

                try:
                    if gc.get("init_super_admin"):
                        # save the version info into the database
                        version_data = JavaBinary(
                            major_version=major_ver,
                            minor_version=minor_ver,
                            bin_directory=os.path.join(root_dir, binary_dir),
                            install_time=datetime.now()
                        )
                        db.session.add(version_data)
                        db.session.commit()
                    else:
                        # TODO store database data into a temporal database
                        pass
                except:
                    # writing database error
                    logging.error(traceback.format_exc())
                    self.tasks_pool.update(hash, status=_utils.FAIL)
                    #download_queue[hash]["status"] = _utils.FAIL
                    # delete scheduler
                    if sch_job != None:
                        sch_job.remove()
                    _send_dw_signal("_download_finish", hash, False)
                    return

                self.tasks_pool.update(hash, status=_utils.FINISH)
                if sch_job != None:
                    sch_job.remove()

                _send_dw_signal("_extract_finish", hash, True)

            def _send_finish_event(download_result, filename):
                # send finish event
                self.tasks_pool.update(hash, status=_utils.FINISH)
                #download_queue[hash]["status"] = _utils.FINISH
                _send_dw_signal("_download_finish", hash, True)

            def _network_error(e):
                self.tasks_pool.update(hash, status=_utils.FINISH)
                #download_queue[hash]["status"] = _utils.FAIL
                _send_dw_signal("_download_finish", hash, False)

            dp = DownloaderPool.getInstance()
            inst, hash = dp.newTask(link, download_dir=download_dir)
            # add cookies to download java directly
            inst.disableSSLCert()
            inst.setHeaders({
                "Cookie": "oraclelicense=accept-securebackup-cookie"
            })
            # Since multi thread is not stable here,
            # we decided to use only one thread to download it
            inst.set_force_singlethread(True)
            # global config
            gc = GlobalConfig.getInstance()
            root_dir = gc.get("lib_bin_dir")

            # add hook
            inst.addDownloadFinishHook(_send_finish_event)
            inst.addDownloadFinishHook(_extract_file)
            inst.addNetworkErrorHook(_network_error)
            dp.start(hash)

            return inst, hash

        try:
            gc = GlobalConfig.getInstance()
            files_dir = gc.get("files_dir")

            major_ver = values.get("major")
            minor_ver = values.get("minor")

            source = sourceJAVA()
            link = source.get_download_link(major_ver, minor_ver)
            binary_dir = source.get_binary_directory(major_ver, minor_ver)

            if link != None:
                if self.tasks_pool.has_working_link(link):
                    _send_dw_signal("_download_start", None, None)
                    return

                # create new task and download
                inst, hash = _add_java_task(link, files_dir, binary_dir)

                self.tasks_pool.add(hash, link)
                #_utils.queue_add(hash, link)
                #download_queue[hash]["status"] = _utils.DOWNLOADING
                # start progress scheduler
                if not self.scheduler.running:
                    self.scheduler.start()

                sch_job = self.scheduler.add_job(_schedule_get_progress, 'interval', seconds=1, args=[self, hash])

                _send_dw_signal("_download_start", hash, None)
            else:
                _send_dw_signal("_download_start", None, None)
        except:
            logging.error(traceback.format_exc())

    def get_active_tasks(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)

        def send_dw_signal(event_name, result):
            ws = WSConnections.getInstance()
            v = {
                "event": event_name,
                "result": result,
                "flag" : flag
            }

            ws.send_data("message",v ,sid=sid)

        active_tasks = self.tasks_pool.get_all()
        send_dw_signal("_active_tasks", active_tasks)

    def terminate_task(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)

        def send_dw_signal(event_name, result):
            ws = WSConnections.getInstance()
            v = {
                "event": event_name,
                "result": result,
                "flag" : flag
            }

            ws.send_data("message",v ,sid=sid)

        hash = values.get("hash")
        if hash == None:
            return
        else:
            dp = DownloaderPool.getInstance()
            dp.terminate(hash)
            send_dw_signal("terminate_task", True)

    def init_download_list(self, flag, values):
        '''
        init a list of all java versions.
        dw_list model:
        {
            "major" : ***,
            "minor" : ***,
            "link" : ***,
            "dw" : {
                "progress",
                "status,
                "current_hash",
            }
        }
        :param flag:
        :param values:
        :return:
        '''
        uid, sid, src, dest = self.pool.get(flag)

        def send_dw_signal(event_name, result):
            ws = WSConnections.getInstance()
            v = {
                "event": event_name,
                "result": result,
                "flag" : flag
            }
            ws.send_data("message",v ,sid=sid)

        source = sourceJAVA()
        _list = source.get_download_list()

        dw_list = []
        for item in _list:
            _dw = {
                "progress": 0.0,
                "status": _utils.WAIT,
                "current_hash": ""
            }
            # get status from cache (to return correct data even if the web page refreshed)
            # for _key in download_queue:
            #    q = download_queue.get(_key)
            #    if q.get("link") == item.get("link"):
            #        _dw["progress"] = q.get("progress")
            #        _dw["status"] = q.get("status")
            #        _dw["current_hash"] = _key

            # fetch active download tasks
            _tasks = self.tasks_pool.get_all()
            for task in _tasks:
                if _tasks[task]["link"] == item.get("link"):
                    _dw["progress"] = _tasks[task]["progress"]
                    _dw["status"] = _tasks[task]["status"]
                    _dw["current_hash"] = task
                    break

            # and fetch from database if there are some versions already installed.
            res = db.session.query(JavaBinary).filter(
                JavaBinary.major_version == str(item.get("major")),
                JavaBinary.minor_version == str(item.get("minor"))
            ).first()
            # that means, this java version has record on the database
            if res != None:
                _dw["status"] = _utils.FINISH

            _model = {
                "major": item.get("major"),
                "minor": item.get("minor"),
                "link": item.get("link"),
                "dw": _dw
            }

            dw_list.append(_model)
        send_dw_signal("_init_download_list", dw_list)
