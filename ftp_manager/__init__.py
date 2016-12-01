from .manager import FTPManager
from .mq_events import FTPAccountEventHandler
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG
PORT = 2121

def start_FTP_manager():
    manager = FTPManager()
    manager.set_port(PORT)
    manager.launch(background=True)

    proxy = MessageQueueProxy(WS_TAG.FTM)
    proxy.register(FTPAccountEventHandler)
    proxy.listen(background=False)
