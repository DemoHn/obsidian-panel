__author__ = "Nigshoxiz"

# import app
from ftm import FTPManager
from ftm.manager import ServerThread

import threading, socket, os
#m = FTPManager(2121)
#m.launch()

#First .py module

from ftm.manager import FTPManager

m =FTPManager(2121)
m.launch()