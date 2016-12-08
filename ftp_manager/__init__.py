from .manager import FTPManager
from .mq_events import FTPAccountEventHandler
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG
from ob_logger import Logger

logger = Logger("FTM")

def start_FTP_manager(port=2121, debug=True):
    logger.set_debug(debug)
    manager = FTPManager()
    manager.set_port(port)
    manager.launch(background=True)

    proxy = MessageQueueProxy(WS_TAG.FTM)
    proxy.register(FTPAccountEventHandler)
    proxy.listen(background=False)
