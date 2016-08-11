__author__ = "Nigshoxiz"

from asyncio import SubprocessProtocol
from . import logger
from . import MCProcessPool

class LogMonitorProtocol(SubprocessProtocol):

    def __init__(self,_port):
        """

        :param _port: server listening port of the process.
        Just used for indexing :-)
        """
        self._port = _port
        self._instance = None
        self.getMCInstance()
        self.__pipe_counter = 0
        pass

    def getMCInstance(self):
        self._instance = MCProcessPool.getInstance().get(self._port)
        pass

    # on data received
    def pipe_data_received(self, fd, data):
        _STATE_RUNNING = 2
        if fd == 1 or fd == 2:
            #logger.debug(self._port+ " - " + data.decode("utf-8"))
            # add callbacks after some particular log exists.

            # run additional function
            self._instance._run_hook("data_received", data)

            if data.decode('utf-8').find("Done") >= 0:
                self._instance._status = _STATE_RUNNING
                self._instance._run_hook("inst_running")


    def pipe_connection_lost(self, fd, exc):
        self.__pipe_counter += 1
        # when stdin, stdout, stderr are all disconnected,
        # it is the time to terminate the thread.
        if self.__pipe_counter == 3:
            self.__pipe_counter = 0
            self._instance._run_hook("connection_lost")
            self._instance.terminate_callback()