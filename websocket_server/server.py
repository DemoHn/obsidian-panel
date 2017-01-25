from app.tools.mq_proxy import WS_TAG, MessageQueueProxy
import socketio, eventlet, json, re, zmq, threading, traceback, engineio
from . import logger

from .ws_conn import WSConnections


def start_zeromq_broker(router_port=852, debug=True):
    logger.set_debug(debug)
    # bind broker port
    context = zmq.Context()
    socket  = context.socket(zmq.ROUTER)
    socket.bind("tcp://*:%s" % router_port)

    logger.debug("Start ZeroMQ broker at %s" % router_port)
    while True:
        try:
            msg = socket.recv_multipart()
            _msg_json = json.loads(msg[1].decode())

            logger.debug("recv msg --> %s" % msg[1].decode())

            # get source type : send-* or recv-*
            src = msg[0].decode()
            forward_dest = _msg_json.get("_dest")

            if src.find("send-") >= 0:
                forward_dest = "recv-" + _msg_json.get("_dest")
            elif src.find("recv-") >= 0:
                forward_dest = "send-" + _msg_json.get("_dest")

            forward_arr = [forward_dest.encode(), msg[1]]
            socket.send_multipart(forward_arr)
        except:
            logger.error(traceback.format_exc())
            continue
