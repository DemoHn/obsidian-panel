__author__ = "Nigshoxiz"

from task_scheduler import Singleton, logger

from app import db
from app.model import JavaBinary
from app.controller.global_config import GlobalConfig
from app.tools.mc_downloader import DownloaderPool, sourceJAVA
from app.tools.mq_proxy import WS_TAG, MessageQueueProxy

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import tarfile
import traceback
import os, json

class _utils:
    WAIT = 1
    DOWNLOADING = 2
    EXTRACTING = 3
    FINISH = 4
    FAIL = 5
    EXTRACT_FAIL= 6

class DownloadingTasksPool(metaclass=Singleton):

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


class DownloadTaskManager(metaclass=Singleton):

    def __init__(self):
        self.proxy      = MessageQueueProxy(WS_TAG.TSR)
        self.tasks_pool = DownloadingTasksPool()
        self.scheduler  = BackgroundScheduler()

    def download_newest_java(self, flag, values):
        s = sourceJAVA()
        list = s.get_download_list()
        # most newest one
        newest_version = list[0]
        self.add_download_java_task(flag, newest_version)

    def add_download_java_task(self, download_link, binary_dir, version_pair, uid):
        gc = GlobalConfig()
        root_dir = gc.get("lib_bin_dir")
        major_ver, minor_ver = version_pair

        '''
            when accessing this route, a new JDK starts downloading in the background.
            Due to the limitation of current technology, we only allow one file to download at the
            same time.
            request params: [POST]
            :major: <major version of java>
            :minor: <minor version of java>
            '''
        def _schedule_get_progress(self, hash):
            # fetch and update data
            dp = DownloaderPool.getInstance()
            _t = dp.get(hash)
            if _t != None:
                inst = _t.dl
                _dw, _filesize = inst.getProgress()
                # update data on download_queue
                if _filesize > 0 and _dw != None and _filesize != None:
                    self.tasks_pool.update(hash, progress=_dw / _filesize)
                    _send_dw_signal("_get_progress", hash, (_dw, _filesize))

        def _send_dw_signal(event_name, hash, result):
            values = {
                "event": event_name,
                "hash": hash,
                "result": result,
                "uid" : uid
            }

            self.proxy.send("websocket.dw_response", values, WS_TAG.CLIENT, reply=False)

        def _extract_file(download_result, filename, version_pair):
            # for abnormal input parameters(like empty filename), the only thing is to terminate
            # next steps!
            if download_result == False or filename == None:
                return None

            logger.debug("Download Result: %s" % download_result)
            logger.debug("Start Extracting File...")

            # send extract_start event
            self.tasks_pool.update(hash, status=_utils.EXTRACTING)
            _send_dw_signal("_extract_start", hash, True)

            # open archive
            archive = tarfile.open(filename)
            try:
                archive.extractall(path=root_dir)
            except:
                archive.close()
                logger.error(traceback.format_exc())
                self.tasks_pool.update(hash, status=_utils.EXTRACT_FAIL)
                # send extract_finish event (when extract failed)
                _send_dw_signal("_extract_finish", hash, False)
                return None

            logger.debug("extract dir: %s, finish!" % root_dir)
            archive.close()

            try:
                # save the version info into the database
                version_data = JavaBinary(
                    major_version=major_ver,
                    minor_version=minor_ver,
                    bin_directory=os.path.join(root_dir, binary_dir),
                    install_time=datetime.now()
                )
                db.session.add(version_data)
                db.session.commit()
            except:
                # writing database error
                logger.error(traceback.format_exc())
                self.tasks_pool.update(hash, status=_utils.FAIL)
                # delete scheduler
                if sch_job != None:
                    sch_job.remove()
                    _send_dw_signal("_download_finish", hash, False)
                    return

                self.tasks_pool.update(hash, status=_utils.FINISH)
                if sch_job != None:
                    sch_job.remove()
                _send_dw_signal("_extract_finish", hash, True)

        def _add_java_task(link, download_dir, binary_dir, version_pair):
            sch_job = None
            '''
            add task of downloading java, with hooks.
            :return: (<instance>, <download_hash>)
            '''

            def _send_finish_event(download_result, filename):
                # send finish event
                self.tasks_pool.update(hash, status=_utils.FINISH)
                _send_dw_signal("_download_finish", hash, True)

            def _network_error(e):
                self.tasks_pool.update(hash, status=_utils.FAIL)
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
            gc = GlobalConfig()
            files_dir = gc.get("files_dir")

            link = download_link
            binary_dir = binary_dir
            # version_pair : (major_version, minor_version)
            # e.g.: (8, 102)
            version_pair = version_pair
            if link != None:
                if self.tasks_pool.has_working_link(link):
                    _send_dw_signal("_download_start", None, None)
                    return

                # create new task and download
                inst, hash = _add_java_task(link, files_dir, binary_dir, version_pair)

                self.tasks_pool.add(hash, link)
                # start progress scheduler
                if not self.scheduler.running:
                    self.scheduler.start()

                sch_job = self.scheduler.add_job(_schedule_get_progress, 'interval', seconds=1, args=[self, hash])

                _send_dw_signal("_download_start", hash, link)
            else:
                _send_dw_signal("_download_start", None, None)
        except:
            logger.error(traceback.format_exc())
