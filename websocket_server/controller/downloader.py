__author__ = "Nigshoxiz"

from websocket_server.server import WSConnections
from app import db
from app.tools.mq_proxy import WS_TAG
from app.model import JavaBinary
from app.controller.global_config import GlobalConfig
from app.tools.mc_downloader import DownloaderPool, sourceJAVA
from app.tools.mq_proxy import MessageEventHandler, WS_TAG, MessageQueueProxy


from datetime import datetime
import logging
import tarfile
import traceback

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


class DownloaderEventHandler(MessageEventHandler):

    __prefix__ = "downloader"
    def __init__(self):

        self.proxy = MessageQueueProxy(WS_TAG.CONTROL)
        self.tasks_pool = DownloadingTasks()

        MessageEventHandler.__init__(self)

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

        def _send_dw_signal(event_name, hash, result):
            ws = WSConnections.getInstance()
            v = {
                "event": event_name,
                "hash": hash,
                "result": result,
                "flag" : flag
            }
            ws.send_data("message", v, sid=sid)

            #event = "%s.%s" % (ControllerOfDownloader.prefix, event_name)
            #self.proxy.send(event, WS_TAG.CLIENT, flag, v)

        def _add_java_task(link, download_dir):
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
                    archive.extractall(path=bin_dir)
                except:
                    archive.close()
                    self.tasks_pool.update(hash, status=_utils.EXTRACT_FAIL)
                    #download_queue[hash]["status"] = _utils.EXTRACT_FAIL
                    # send extract_finish event (when extract failed)
                    _send_dw_signal("_extract_finish", hash, False)
                    return None

                logging.debug("extract dir: %s, finish!" % bin_dir)
                archive.close()

                try:
                    # save the version info into the database
                    version_data = JavaBinary(
                        major_version=major_ver,
                        minor_version=minor_ver,
                        bin_directory=bin_dir,
                        install_time=datetime.now()
                    )
                    db.session.add(version_data)
                    db.session.commit()
                except:
                    # writing database error
                    logging.error(traceback.format_exc())
                    self.tasks_pool.update(hash, status=_utils.FAIL)
                    #download_queue[hash]["status"] = _utils.FAIL
                    _send_dw_signal("_download_finish", hash, False)

                self.tasks_pool.update(hash, status=_utils.FINISH)
                #download_queue[hash]["status"] = _utils.FINISH
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
            bin_dir = gc.get("lib_bin_dir")

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

            if link != None:
                # create new task and download
                inst, hash = _add_java_task(link, files_dir)

                self.tasks_pool.add(hash, link)
                #_utils.queue_add(hash, link)
                #download_queue[hash]["status"] = _utils.DOWNLOADING
                _send_dw_signal("_download_start", hash, None)
            else:
                _send_dw_signal("_download_start", None, None)
        except:
            logging.error(traceback.format_exc())

    def request_task_progress(self, flag, values):
        uid, sid, src, dest = self.pool.get(flag)
        hash = values.get('hash')

        def send_dw_signal(event_name, hash, result):
            ws = WSConnections.getInstance()
            v = {
                "event": event_name,
                "hash": hash,
                "result": result,
                "flag" : flag
            }
            ws.send_data("message", v, sid=sid)

        # fetch and update data
        dp = DownloaderPool.getInstance()
        _t = dp.get(hash)
        if _t != None:
            inst = _t.dl
            _dw, _filesize = inst.getProgress()

            # update data on download_queue
            if _filesize > 0 and \
                            _dw != None and _filesize != None:
            #    download_queue[hash]["progress"] = _dw / _filesize
            #_utils.send_dw_signal("_get_progress", hash, (_dw, _filesize))
                self.tasks_pool.update(hash, progress= _dw / _filesize)
                send_dw_signal("_get_progress", hash, (_dw, _filesize))

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
        send_dw_signal("_active_tasks", active_taskss)


