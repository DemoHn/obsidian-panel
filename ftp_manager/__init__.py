from .manager import FTPManager
from .mq_events import FTPAccountEventHandler
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG
from ob_logger import Logger

logger = Logger("FTM")

def start_FTP_manager(port=21, debug=True, zmq_port=852):
    logger.set_debug(debug)

    proxy = MessageQueueProxy(WS_TAG.FTM, router_port=zmq_port)
    proxy.register(FTPAccountEventHandler)
    proxy.listen(background=True)

    manager = FTPManager()
    manager.set_port(port)

    logger.info("This is FTP Manager, listening port %s" % port)
    manager.launch(background=False)
