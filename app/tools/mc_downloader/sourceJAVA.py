from app.tools.cpuinfo import cpu
import platform

class sourceJAVA(object):
    '''
    get & download java binary file
    '''


    def __init__(self):
        self._arch = self._get_cpu_arch()
        self._OS   = self._get_OS()
        # KEY : <priority>
        # VALUE : <many objs>
        self.versions = {
            "5": {
                'major': "8", "minor": "102",
                "arch": {
                    "x86": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/8u102-b14/jdk-8u102-linux-i586.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/8u102-b14/jdk-8u102-windows-i586.exe"
                    },
                    "x64": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/8u102-b14/jdk-8u102-linux-x64.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/8u102-b14/jdk-8u102-windows-x64.exe"
                    }
                }
            },
            "4": {
                'major': "8", "minor": "101",
                "arch": {"x86": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/8u101-b13/jdk-8u101-linux-i586.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/8u101-b13/jdk-8u101-windows-i586.exe"
                    },"x64": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/8u101-b13/jdk-8u101-linux-x64.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/8u101-b13/jdk-8u101-windows-x64.exe"
                    }
                }
            },
            "3": {
                'major': "7", "minor": "80",
                "arch": {
                    "x86": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/7u80-b15/jdk-7u80-linux-i586.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/7u80-b15/jdk-7u80-windows-i586.exe"
                    },
                    "x64": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/7u80-b15/jdk-7u80-linux-x64.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/7u80-b15/jdk-7u80-windows-x64.exe"
                    }
                }
            },
            "2": {
                'major': "7", "minor": "79",
                "arch": {
                    "x86": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-linux-i586.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-windows-i586.exe"
                    },
                    "x64": {
                        "linux": "http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-linux-x64.tar.gz",
                        "windows": "http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-windows-x64.exe"
                    }
                }
            }
        }

    def _get_cpu_arch(self):
        if cpu._is_64bit():
            return "x64"
        else:
            return "x86"

    def _get_OS(self):
        system = platform.system()

        if system == "Windows":
            return "windows"
        elif system == "Linux":
            return "linux"
        else:
            return "linux"


    def __add_version_info__(self, priority, version_config):
        '''
        If there are new versions of JDK (like java 9), advanced users could use this function to
        'monkey patch' it!

        :param priority:
        :param version_config:
        FORMAT:
        {
           "major" : <Java major version>,
           "minor" : <java minor version>,
           "arch" : {
               "x86" : {
                   "linux" : <linux x86 link>,
                   "window" : <window x86 link>
                   # I bet nobody use Mac OS or Solaris as host OS of his server
               },
               "x64": {
                   "linux" : <linux x64 link>,
                   "window" : <window x64 link>
               }
           }
        }
        '''
        priority = str(priority)
        self.versions[priority] = version_config
