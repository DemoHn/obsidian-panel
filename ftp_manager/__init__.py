from .manager import FTPManager
from .mq_events import FTPAccountEventHandler
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG
from app.utils import is_debug, read_config_yaml
from ob_logger import Logger

logger = Logger("FTM", debug = is_debug())

def start_FTP_manager():

    _config = read_config_yaml()
    zmq_port = _config['broker']['listen_port']
    port = _config['ftp']['listen_port']

    proxy = MessageQueueProxy(WS_TAG.FTM, router_port=zmq_port)
    proxy.register(FTPAccountEventHandler)
    proxy.listen(background=True)

    manager = FTPManager()
    manager.set_port(port)

    logger.info("This is FTP Manager, listening port %s" % port)
    manager.launch(background=False)
