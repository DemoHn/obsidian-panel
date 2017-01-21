from app.tools.mq_proxy import WS_TAG, MessageQueueProxy
import socketio, eventlet, json, re, zmq, threading, traceback
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

def start_websocket_server(debug=True, port=851, router_port=852):
    logger.set_debug(debug)

    # start proxy
    from .mq_events import WebsocketEventHandler
    proxy = MessageQueueProxy(WS_TAG.CLIENT)
    proxy.register(WebsocketEventHandler)
    proxy.listen(background=True)

    eventlet.monkey_patch()

    mgr = socketio.RedisManager("redis://")
    sio = socketio.Server(client_manager=mgr)

    #init
    ws = WSConnections.getInstance(sio)
    ws.init_events()
    app = socketio.Middleware(sio)

    logger.info("This is Websocket Server.")
    logger.info("The listening port is %s" % port)
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', port)), app)
