__author__ = "Nigshoxiz"
from urllib.error import HTTPError
from urllib.request import urlopen, Request
import threading
import shutil
import traceback
import json
import os
import ssl

class Downloader(object):

    def __init__(self,url, force_multithread=False , force_singlethread=False):
        self.url = url
        self.filesize = 0
        self.support_range = False
        self.timeout = 5
        self.threads = []

        self.lock = threading.Lock()

        self.force_multithread  = force_multithread
        self.force_singlethread = force_singlethread

        self.dw_type_flag = None
        self.download_correct_flag = True
        self.slices = []

        # urlopen's ctx
        self.ctx = None
        self.headers = {}
        try:
            self.filename = self.url.split("/")[-1]
            _ , __ = self.readReport()
            if __ == None:
                self.fd = open(self.filename + ".tmp", "wb")
            else:
                self.fd = open(self.filename + ".tmp", "r+b")
        except:
            self.fd.close()

        self.THREADS_NUM = 8

    def __del__(self):
        self.fd.close()

    def analyse(self,headers):
        req = Request(url=self.url, method="HEAD")
        req.add_header("Range","bytes=0-")

        for i in headers:
            req.add_header(i, headers.get(i))
        try:
            result = urlopen(req)

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

    def setHeaders(self,headers):
        self.headers = headers

    def disableSSLCert(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        self.ctx = ctx

    def getProgress(self):
        """
        get downloaded size of file
        :return:
        """
        if self.dw_type_flag == "single":
            if os.path.exists(self.filename+".tmp"):
                _size = os.path.getsize(self.filename+".tmp")
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

    def makeReport(self,slices):
        # generate *.report file when download process is abnormally terminated.
        # it is a json file , like:
        # {
        #   "support_range" : True | False,
        #   "slices": [(<index,file_size>)]
        # }
        # slices = None when ranging download is not supported.
        rtn = {
            "support_range": self.support_range,
            "slices": slices
        }
        f = open(self.filename+".report", "w+")
        f.write(json.dumps(rtn))
        f.close()

    def readReport(self):
        _filename = self.filename+".report"

        if os.path.isfile(_filename):
            f = open(_filename,"r")
            try:
                r = json.loads(f.read())
                return r.get("support_range") , r.get("slices")
            except:
                return None, None
        else:
            return None, None

    def download(self):
        def __download_singlethread():
            print("[MC Downloader] directly downloading...")
            self.dw_type_flag = "single"
            try:
                req = Request(url=self.url, headers=self.headers)
                resp = urlopen(req, context=self.ctx)

                if self.filesize < 0:
                    _header = resp.info()
                    _len = _header.get("Content-Length")
                    self.filesize = _len
                #self.fd.write(resp.read())
                shutil.copyfileobj(resp, self.fd)
                '''
                while True:
                    buffer = resp.read(1024)
                    if not buffer:
                        break
                    self.fd.write(buffer)
                '''
            except HTTPError:
                print("HTTP error.")
                return False
            except:
                traceback.print_exc()
                print("error")
                return False

            return True

        def __download_multithread():
            self.dw_type_flag = "multi"
            _, slices = self.readReport()
            __exists  = os.path.exists(self.filename+".tmp")

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
                ranges = self.splitRange()

            print("[MC downloader] Start Downloading... threads = %s" % len(ranges))
            _i = 0
            for threads in range(len(ranges)):
                self.slices.append([ranges[_i][0], 0, ranges[_i][1]])

                range_item = ranges[_i]
                t = threading.Thread(target=self.downloadThread, args=(range_item, _i))
                t.setDaemon(True)
                t.start()
                self.threads.append(t)
                _i += 1

            try:
                for t in self.threads:
                    t.join()
            except KeyboardInterrupt:
                self.makeReport(self.slices)
                return False

            if self.download_correct_flag == True:
                return True
            else:
                self.makeReport(self.slices)
                return False
        # get filesize, Partial Support, etc.
        self.analyse(self.headers)

        if self.force_multithread:
            res = __download_multithread()
        elif self.force_singlethread:
            res = __download_singlethread()
        else:
            if self.support_range == True:
                res = __download_multithread()
            else:
                res = __download_singlethread()

        if res:
            shutil.move(self.filename+".tmp",self.filename)
            if os.path.exists(self.filename+".report"):
                os.remove(self.filename+".report")
        return res

    def splitRange(self):
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


def downloadThread(self, range_item, _index):
    MAX_RETRY = 3

    req = Request(url=self.url)
    req.add_header("Range", "bytes=%s-%s" % range_item)
    # add header
    for i in self.headers:
        req.add_header(i, self.headers.get(i))
    retry = 0
    while True:
        try:
            resp = urlopen(req, timeout=self.timeout, context=self.ctx)
            # add lock
            self.lock.acquire()
            print("range = %s-%s" % (range_item))
            self.fd.seek(range_item[0], 0)

            while 1:
                buf = resp.read(16 * 1024)
                if not buf:
                    break
                self.fd.write(buf)
                self.slices[_index][1] += len(buf)

            # shutil.copyfileobj(resp, self.fd)
            print("%s finished!" % threading.current_thread().getName())
            self.lock.release()

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