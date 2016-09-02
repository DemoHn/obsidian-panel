__author__ = "Nigshoxiz"
import os
import re

class KVParser(object):
    """
    A general Key-Value Parser
    Parsed File Format :

    # this is comment
    server-ip=12.23.43.3
    motd=This is a Minecraft Server # inline comment

    """
    def __init__(self,file):
        """
        :param file: filename being parsed.
        """
        self.conf_items = {}
        self.file = file

    def loads(self):
        """
        read the whole config file and make config index
        :return:
        """
        fd = open(os.path.normpath(self.file),"r")

        if fd == None:
            raise FileNotFoundError
        for line in fd.readlines():
            if line.find("#") == 0:
                continue
            else:
                pattern = "^([a-zA-Z\-_ ]+)=([^#]*)"
                result  = re.match(pattern,line)
                if result != None:
                    key = result.group(1)
                    val = result.group(2).strip()
                    self.conf_items[key] = val

        fd.close()

    def dumps(self):
        file_content = []
        for item in self.conf_items:
            file_content.append("%s=%s" %(str(item), str(self.conf_items[item]) ))

        content = "\n".join(file_content)
        fd = open(os.path.normpath(self.file),"w+")
        fd.write(content)
        fd.close()

    def add(self,key,value):
        if self.conf_items.get(key) == None:
            self.conf_items[key] = value

    def remove(self,key):
        del self.conf_items[key]

    def replace(self,key,new_value):
        self.conf_items[key] = new_value

    def get(self,key):
        return self.conf_items[key]

class ServerPropertiesParser(KVParser):
    """
    This class loads & modifies MC server's `server.properties` file.
    The config file is formatted like [Key]=[Value].

    Notice : Some Config entries will be checked specially or converted.
    """
    def __init__(self,file):
        """
        :param file: file being parsed
        """
        super(ServerPropertiesParser,self).__init__(file)
        self.motd = "A Minecraft Server"
        self.server_port = 25565
        self.level_name = "world"

        self.loads()
        self.add("motd", self.motd)
        self.add("server-port", self.server_port)
        self.add("level-name", self.level_name)

    def write_config(self, config):
        for k in config:
            if k == "motd":
                self.set_motd(config[k])
            elif k == "server-port":
                self.set_server_port(config[k])
            elif k == "level-name":
                self.set_server_port(config[k])

        self.dumps()

    def set_motd(self,motd):
        """
        :param motd: motd data (server's welcome words.) encoded in utf-8
        colored text (like §a) is also supported
        :return:
        """
        # get each
        motd_arr = []
        for motd_char in motd:
            char_num = ord(motd_char)
            # 小于128，则不转码
            if char_num < 128 and char_num != ord('\\'):
                motd_arr.append(motd_char)
            else:
                # 大于128，则转成 \uXXXX 格式
                s = '\\u' + str(hex(motd_char))[2:]
                motd_arr.append(s)

        self.replace("motd","".join(motd_arr))

    def get_motd(self):
        _motd_str = self.get("motd")

        _len = len(_motd_str)
        _index = 0

        _rtn_str = ""
        while True:

            if _index == _len:
                break

            if _motd_str[_index] == "\\" and \
                    ( _motd_str[_index+1] == "u" or _motd_str[_index+1] == "U") and \
                    _index + 5 < _len:
                _num = int(_motd_str[_index+2]) * 4096 + \
                       int(_motd_str[_index+3]) * 256 + \
                       int(_motd_str[_index+4]) * 16 + \
                       int(_motd_str[_index+5])
                _rtn_str += chr(_num)
                _index += 6
                continue
            else:
                _rtn_str += _motd_str[_index]
                _index += 1

    def set_server_port(self, server_port):
        # server_port range : [1,65535]
        server_port = int(server_port)
        if server_port >= 1 and server_port <= 65535:
            self.add("server-port",str(server_port))

    def set_level_name(self, level_name):
        pass