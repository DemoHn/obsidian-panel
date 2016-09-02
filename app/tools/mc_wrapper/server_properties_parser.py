__author__ = "Nigshoxiz"
import os
import re
from . import logger

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
        fd = open(os.path.normpath(self.file),"r+")

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
            _k = str(k).replace("-","_")
            _attr_name = "set_%s" % _k
            if hasattr(self, _attr_name):
                func = getattr(self, _attr_name)
                func(config[k])

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
                s = '\\u' + str(hex(char_num))[2:]
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
            self.replace("server-port",str(server_port))
        else:
            raise Exception("the value '%s' is out of range!" % server_port)

    def set_level_name(self, level_name):
        self.replace("level-name",str(level_name))
        pass

    def set_max_players(self, max_players):
        # max_players must > 0
        _max_players = int(max_players)

        if _max_players > 0:
            self.replace("max-players",str(max_players))
        else:
            raise Exception("the value '%s' is out of range!" % max_players)

    def set_online_mode(self, online_mode):
        '''
        :param online_mode: If set to True, players must login the server with MOJANG account,
        (i.e. only legal players could enter the server)
        value : True or False.
        :return: nothing
        '''
        if online_mode == True:
            self.replace("online-mode","true")
        else:
            self.replace("online-mode","false")

    def set_difficulty(self, difficulty):
        '''
        According to Minecraft Wiki, the difficulty property should be an integer
        in the set {0,1,2,3}. Each number represents for different level:
        0 - Peaceful
        1 - Easy
        2 - Normal
        3 - Hard

        If user still provide an integer that exceed the set above, we only print
        a warning message, since it may be acceptable on other unofficial version
        of MC server core.

        :param difficulty: a number
        :return: nothing
        '''
        difficulty = int(difficulty)
        num_set = (0,1,2,3)

        if difficulty not in num_set:
            logger.warning("The difficulty level '%s' may not work." % difficulty)

        self.replace("difficulty", str(difficulty))