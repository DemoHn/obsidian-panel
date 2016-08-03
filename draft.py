__author__ = "Nigshoxiz"

from app.tools.mc_downloader import Downloader
from app.controller.config_env import DatabaseEnv, JavaEnv
config = {
    "jar_file" : "/home/demohn/spigot-1.7.10-SNAPSHOT-b1652.jar",
    "proc_cwd" : "/data/hello/E",
}

_kwargs = {
    "jar_file" : "/home/demohn/spigot-1.7.10-SNAPSHOT-b1652.jar",
    "proc_cwd" : "/data/hello/F",
}

#t = MCServerInstanceThread(12344,config=config)
#t.start()

#u = Downloader("http://mirrors.zju.edu.cn/debian/indices/Maintainers")
#u = Downloader("http://mirrors.zju.edu.cn/debian/README.mirrors.html", force_multithread=True)
#u = Downloader("https://ftp.gnu.org/gnu/gcc/gcc-2.8.1.tar.gz", force_singlethread=False)

u = Downloader("http://download.oracle.com/otn-pub/java/jdk/8u92-b14/jdk-8u92-linux-x64.tar.gz")
u.disableSSLCert()
u.setHeaders({
   "Cookie": "oraclelicense=accept-securebackup-cookie"
})
#print(u.download())

j = JavaEnv()
print(j.findSystemJavaInfo())


