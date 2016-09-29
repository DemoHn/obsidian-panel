__author__ = "Nigshoxiz"

'''
[circus]
endpoint = tcp://127.0.0.1:5555
pubsub_endpoint = tcp://127.0.0.1:5556
stats_endpoint = tcp://127.0.0.1:5557

[watcher:web]
copy_env = True
virtualenv = ./env
working_dir = ./

use_sockets = True
cmd = ./env/bin/chaussette run.app
args = --fd $(circus.sockets.web) --backend eventlet
numprocesses = 5

[socket:web]
host = 0.0.0.0
port = 5000
'''

# Dev Note:
# For some strange reasons, it is not allowed to run a chaussette instance
# using eventlet backend in python3 (chaussette version: v0.13.0, which is the newest version pip could download).
# That is, we can't run `chaussette run.app --backed eventlet` to start server directly.
# In fact, chaussette supports eventlet backend in python3 internally, it just denies `eventlet` as an option
# of `--backend` in command line. Considering the stability of eventlet library in python3, which has been
# improved a lot since the release date of chaussette v0.13.0 (2015), we monkey-patch it to bypass the
# restriction of command line .
#
# And How to run in circus?
#
# Just append the following configuration:
#
# [watcher:xxx]
# cmd = python start_chaussette.py --fd $(circus.sockets.web)
#
# Nigshoxiz
# 2016-8-16

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