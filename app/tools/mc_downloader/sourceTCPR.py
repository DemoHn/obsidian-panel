__author__ = "Nigshoxiz"

from urllib.request import urlopen, Request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import traceback

class TCPRfilters(object):
    def __init__(self):
        self.list = []

    def filter(self, serv_type, html_content):
        serv_type = serv_type.lower()
        self.parsed = BeautifulSoup(html_content, "html.parser")

        if serv_type == "bukkit" or \
            serv_type == "spigot" or \
            serv_type == "craftbukkit" or \
            serv_type == "paperspigot":
            return self.filter_bukkit()
        pass

    def filter_general(self):
        tables = self.parsed.find_all("table")
        _list = tables[1].tbody.find_all("tr")

        for _td in _list:
            self.list.append(_td.find_all("a")[1]["href"])

    # spigot or bukkit
    def filter_bukkit(self):
        tables = self.parsed.find_all("table")
        _list = tables[1].tbody.find_all("tr")
        filename_re = "^(bukkit|spigot|craftbukkit|PaperSpigot)\-([0-9\.]*)\-(.*)\.jar$"

        for _td in _list:
            filename = _td.find("td").get_text()
            g = re.match(filename_re, filename)
            if g != None:
                _model = {
                    "version": g.group(3),
                    "mc_version":g.group(2),
                    "file_name":filename,
                    "file_url": _td.find_all("a")[1]["href"]
                }
                self.list.append(_model)

        return self.list

    # TODO wait Yive's confirmation of sponge and vanilla page
    def filter_forge(self):
        tables = self.parsed.find_all("table")
        _list = tables[1].tbody.find_all("tr")
        filename_re = "^(bukkit|spigot|craftbukkit|PaperSpigot)\-([0-9\.]*)\-(.*)\.jar$"

        for _td in _list:
            filename = _td.find("td").get_text()
            g = re.match(filename_re, filename)
            if g != None:
                _model = {
                    "version": g.group(3),
                    "mc_version":g.group(2),
                    "file_name":filename,
                    "file_url": _td.find_all("a")[1]["href"]
                }
                self.list.append(_model)

        return self.list

class sourceTCPR(TCPRfilters):
    def __init__(self,url = "https://tcpr.ca"):
        TCPRfilters.__init__(self)
        self.url = url

        self.__list = (
            "vanilla",
            # bukkit
            "bukkit",
            "spigot",
            "craftbukkit",
            "paperspigot",
            # forge
            "mcpc+",
            "sponge",
            "thermos",
            "cauldron"
        )

    def use_proxy(self, proxy_type, host, port):
        import socks
        import socket

        __proxy_type = socks.SOCKS5
        if proxy_type == "socks4":
            __proxy_type = socks.SOCKS4
        elif proxy_type == "socks5":
            __proxy_type = socks.SOCKS5
        elif proxy_type == "http":
            __proxy_type = socks.HTTP

        socks.set_default_proxy(__proxy_type, host, 1080)
        socket.socket = socks.socksocket
        pass

    def retrieve_page(self, route):
        _url = urljoin(self.url, route)
        try:
            _str = ""
            req = Request(url = _url)
            req.add_header("User-Agent",
                           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36")
            resp = urlopen(req)

            while True:
                buffer = resp.read(16*1024)
                if not buffer:
                    break
                _str += buffer.decode()

            return _str
        except:
            return None

    def get_list(self,mc_type):
        _type = ""
        list = []
        if mc_type.lower() == "mcpc+":
            _type = "mcpc"
        else:
            if mc_type.lower() in self.__list:
                _type = mc_type.lower()

        _route = "downloads/%s" % _type
        html = self.retrieve_page(_route)

        if html == None:
            return list
        else:
            print(self.filter("bukkit",html))
            return list