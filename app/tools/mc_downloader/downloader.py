__author__ = "Nigshoxiz"
from urllib.error import HTTPError
from urllib.request import urlopen, Request
import threading
import shutil
import traceback
import json
import os
import ssl
import inspect
import random
import string
import copy

class DownloaderPool(object):

    instance = None
    def __init__(self):
        self.pool = {}

        pass

    @staticmethod
    def getInstance():
        if DownloaderPool.instance == None:
            DownloaderPool.instance = DownloaderPool()
        return DownloaderPool.instance

    def newTask(self, url, **kwargs):
        """
        :param downloader_instance:
        :return: (instance, instance hash)
        """
        def _finish(e):
            print("hook")
            self.remove(_hash)

        dt_inst = DownloaderThread(url, **kwargs)
        dt_inst.dl.addDownloadFinishHook(_finish)

        _hash = dt_inst.hash()
        self.pool[_hash] = dt_inst
        return (dt_inst.dl, _hash)

    def get(self, downloader_hash):
        return self.pool.get(downloader_hash)

    def remove(self, downloader_hash):
        _inst = self.pool.get(downloader_hash)
        if _inst != None:
            _inst.dl.__del__()
            del self.pool[downloader_hash]

    def start(self, downloader_hash):
        _inst = self.pool.get(downloader_hash)
        _inst.setDaemon(True)
        # just start a thread
        _inst.start()

    def pause(self, downloader_hash):
        _inst = self.pool.get(downloader_hash)
        if _inst != None:
            _inst.dl._make_report()
            _inst.stop()

    def terminate(self, downloader_hash):
        _inst = self.pool.get(downloader_hash)
        if _inst != None:
            _inst.stop()
            _inst.dl.clear()
            self.remove(downloader_hash)

    # TODO fix it!!
    def resume(self, downloader_hash):

        _inst = self.pool.get(downloader_hash)

        if _inst.stopped() != True:
            _inst.stop()

        if _inst != None:
            # copy Downloader object
            _dl_obj = copy.copy(_inst.dl)
            # remove old thread
            self.remove(downloader_hash)
            new_dt_inst = DownloaderThread('',_dl = _dl_obj)
            self.pool[downloader_hash] = new_dt_inst
            new_dt_inst.start()
        pass


class DownloaderThread(threading.Thread):

    def __init__(self, url, _dl = None, **kwargs):
        super(DownloaderThread, self).__init__()

        if isinstance(_dl, Downloader):
            self.dl = _dl
            self.dl._reopen_file()
        else:
            self.dl = Downloader(url, **kwargs)

        self._stopper = threading.Event()
        self._can_run = threading.Event()

    def run(self):
        self.dl.download()

    def stop(self):
        self._stopper.set()

    def stopped(self):
        self._stopper.isSet()

    def hash(self):
        return self.dl.__hash__()

class Downloader(object):

    def __init__(self, url, force_multithread=False , force_singlethread=False, download_dir=""):
        self.url = url
        self.filesize = 0
        self.support_range = False
        self.timeout = 5
        self.threads = []

        self.lock = threading.Lock()

        self.force_multithread  = force_multithread
        self.force_singlethread = force_singlethread
        self.download_dir = download_dir

        self.dw_type_flag = None
        self.download_correct_flag = True
        self.slices = []

        self.THREADS_NUM = 8

        self._download_finish_hook = []
        self._network_error_hook = []

        # SSL context
        self.ssl_ctx = None
        self.headers = {}

        # response
        try:
            # get filename from url
            self.filename = self.url.split("/")[-1]
            _tmp_file = os.path.join(self.download_dir, self.filename + ".tmp")
            _, __ = self._read_report()
            if __ == None:
                self.fd = open(_tmp_file, "wb")
            else:
                self.fd = open(_tmp_file, "r+b")
        except:
            self.fd.close()

    # del constructor. After all, all d
    def __del__(self):
        self.fd.close()

    def __hash__(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))

    def setThreads(self,thread_num):
        """
        indicate the number of creating threads when using
        multithread download mode.
        :param thread_num: the number of threads to create. Default is 8.
        :return:
        """
        self.THREADS_NUM = thread_num

    def setHeaders(self,headers):
        self.headers = headers

    def analyse(self,headers):
        req = Request(url=self.url, method="HEAD")
        req.add_header("Range","bytes=0-")

        for i in headers:
            req.add_header(i, headers.get(i))
        try:
            print("start analysing URL...")
            result = urlopen(req, timeout=30)

            headers = result.info()
            _len = headers.get("Content-Length")

            if _len == None:
                self.filesize = -1
            else:
                self.filesize = int(_len)

            if result.getcode() == 206:
                self.support_range = True
            else:
                self.support_range = False

        except:
            self.support_range = False
            self.filesize = -1

    def disableSSLCert(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.ssl_ctx = ctx

    # just a wrapper :-)
    def addDownloadFinishHook(self,fn):
        if inspect.isfunction(fn):
            self._download_finish_hook.append(fn)

    # terminate downloading and remove tmp file
    # WARNING : this operation will remove tep file PERMANENTLY!
    def clear(self):
        _tmp_file = os.path.join(self.download_dir, self.filename + ".tmp")
        _report_file = os.path.join(self.download_dir, self.filename + ".report")
        if os.path.exists(_tmp_file):
            os.remove(_tmp_file)

        if os.path.exists(_report_file):
            os.remove(_report_file)

        pass

    def getProgress(self):
        """
        get downloaded size of file
        :return:
        """
        if self.dw_type_flag == "single":
            _tmp_file = os.path.join(self.download_dir, self.filename + ".tmp")
            if os.path.exists(_tmp_file):
                _size = os.path.getsize(_tmp_file)
                return (_size, self.filesize)
            else:
                return (0, self.filesize)
        elif self.dw_type_flag == "multi":
            _total = 0
            for si in self.slices:
                _total += si[1]
            return (_total, self.filesize)
        else:
            return (None, self.filesize)

    def _make_report(self):
        _report_file = os.path.join(self.download_dir, self.filename + ".report")
        # generate *.report file when download process is abnormally terminated.
        # it is a json file , like:
        # {
        #   "support_range" : True | False,
        #   "slices": [(<index,file_size>)]
        # }
        # slices = None when ranging download is not supported.
        rtn = {
            "support_range": self.support_range,
            "slices": self.slices
        }
        f = open(_report_file, "w+")
        f.write(json.dumps(rtn))
        f.close()

    def _read_report(self):
        _filename = os.path.join(self.download_dir, self.filename+".report")

        if os.path.isfile(_filename):
            f = open(_filename,"r")
            try:
                r = json.loads(f.read())
                return r.get("support_range") , r.get("slices")
            except:
                return None, None
        else:
            return None, None

    # when fd has been abruptly closed, this function is to recover it
    def _reopen_file(self):
        try:
            # get filename from url
            self.filename = self.url.split("/")[-1]
            _tmp_file = os.path.join(self.download_dir, self.filename + ".tmp")
            _ , __ = self._read_report()
            if __ == None:
                self.fd = open(_tmp_file, "wb")
            else:
                self.fd = open(_tmp_file, "r+b")
        except:
            self.fd.close()

    def download(self):
        def _download_singlethread():
            print("[MC Downloader] directly downloading...")
            self.dw_type_flag = "single"
            try:
                req = Request(url=self.url, headers=self.headers)
                resp = urlopen(req, context=self.ssl_ctx)

                if self.filesize < 0:
                    _header = resp.info()
                    _len = _header.get("Content-Length")
                    self.filesize = _len
                #self.fd.write(resp.read())
                shutil.copyfileobj(resp, self.fd,length=8*1024)

            except HTTPError:
                return False
            except:
                return False
            return True

        def _download_multithread():
            self.dw_type_flag = "multi"
            _, slices = self._read_report()
            _tmp_file = os.path.join(self.download_dir, self.filename + ".tmp")
            __exists  = os.path.exists(_tmp_file)

            ranges = []
            if slices != None and __exists == True:
                for item in slices:
                    item[0] = int(item[0])
                    item[1] = int(item[1])
                    item[2] = int(item[2])

                    if item[0] + item[1] - 1 < item[2]:
                        ranges.append( (item[0] + item[1], item[2]) )
                print("[MC downloader] Resume Downloading...")
            else:
                ranges = self._split_range()

            print("[MC downloader] Start Downloading... threads = %s" % len(ranges))
            _i = 0
            for threads in range(len(ranges)):
                self.slices.append([ranges[_i][0], 0, ranges[_i][1]])

                range_item = ranges[_i]
                t = threading.Thread(target=self.download_thread, args=(range_item, _i))
                t.setDaemon(True)
                t.start()
                self.threads.append(t)
                _i += 1

            try:
                for t in self.threads:
                    t.join()
            except KeyboardInterrupt:
                self._make_report()
                return False

            if self.download_correct_flag == True:
                return True
            else:
                self._make_report()
                return False
        # get filesize, Partial Support, etc.
        self.analyse(self.headers)

        if self.force_multithread:
            result = _download_multithread()
        elif self.force_singlethread:
            result = _download_singlethread()
        else:
            if self.support_range == True:
                result = _download_multithread()
            else:
                result = _download_singlethread()

        # after file is successfully downloaded
        if result:
            __repeat_file_counter = 0
            _fn = os.path.join(self.download_dir, self.filename)
            _filename = _fn
            while True:
                if os.path.exists(_filename):
                    __repeat_file_counter += 1
                    _filename = _fn + "." + str(__repeat_file_counter)
                else:
                    _tmp_file = _fn + ".tmp"
                    shutil.move(_tmp_file, _filename)
                    break

            _report_file = os.path.join(self.download_dir, self.filename + ".report")
            if os.path.exists(_report_file):
                os.remove(_report_file)

            # run finish hook
            for _hook in self._download_finish_hook:
                if inspect.isfunction(_hook):
                    _hook(True)
        else:
            # run finish hook
            for _hook in self._download_finish_hook:
                if inspect.isfunction(_hook):
                    _hook(False)
        return result

    def _split_range(self):
        onceDownloadSize = int(self.filesize / self.THREADS_NUM)
        ranges = []
        _index = 0

        while True:
            if _index + onceDownloadSize * 2 > self.filesize:
                ranges.append((_index, self.filesize - 1))
                break
            else:
                ranges.append((_index, _index + onceDownloadSize - 1))
                _index += onceDownloadSize

        return ranges

    def download_thread(self, range_item, _index):
        MAX_RETRY = 5

        req = Request(url=self.url)
        req.add_header("Range", "bytes=%s-%s" % range_item)
        # add header
        for i in self.headers:
            req.add_header(i, self.headers.get(i))

        retry = 0
        while True:
            try:
                print(self.ssl_ctx)
                resp = urlopen(req, timeout=self.timeout, context=self.ssl_ctx)

                # slices format: [<start size>, <downloaded size>,<end size>]
                _download_slice = self.slices[_index][1]

                _range_item = [0, 0]
                if self.slices[_index][1] == 0:
                    _range_item[0] = range_item[0]
                    _range_item[1] = range_item[1]
                else:
                    _range_item[0] = range_item[0] + _download_slice
                    _range_item[1] = range_item[1]
                print("range = %s-%s" % (_range_item[0], _range_item[1]))

                # add lock
                self.lock.acquire()
                self.fd.seek(range_item[0] + _download_slice, 0)
                self.lock.release()

                while True:
                    buf = resp.read(8 * 1024)
                    if not buf:
                        break

                    self.lock.acquire()
                    self.fd.write(buf)
                    self.lock.release()

                    self.slices[_index][1] += len(buf)

                # shutil.copyfileobj(resp, self.fd)
                print("%s finished!" % threading.current_thread().getName())

                break
            except TypeError:
                traceback.print_exc()
                if self.lock.locked():
                    self.lock.release()

                self.download_correct_flag = False
                break
            except:
                traceback.print_exc()
                print("%s - HTTP connection error %s - %s" % (
                    threading.current_thread().getName(), range_item[0], range_item[1]))
                retry += 1
                if retry <= MAX_RETRY:
                    print("retry %s time" % retry)

                if self.lock.locked():
                    self.lock.release()

            if retry == MAX_RETRY + 1:
                self.download_correct_flag = False
                break