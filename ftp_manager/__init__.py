from .manager import FTPManager
from .mq_events import FTPAccountEventHandler
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG
import time
PORT = 2121
def start_FTP_manager():
    proxy = MessageQueueProxy(WS_TAG.FTM)
    proxy.register(FTPAccountEventHandler)
    proxy.listen(background=True)

    manager = FTPManager()
    manager.set_port(PORT)
    manager.launch()

    while True:
        time.sleep(1)
