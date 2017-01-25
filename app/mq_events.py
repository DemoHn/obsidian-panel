from app.tools.mq_proxy import WS_TAG, MessageQueueProxy, MessageEventHandler
from app import db

from websocket_server.ws_conn import WSConnections
class WebsocketEventHandler(MessageEventHandler):

    __prefix__ = "websocket"

    def __init__(self):
        MessageEventHandler.__init__(self)

    # broadcast data pushed from Process Watcher
    def proc_broadcast(self, flag, values):
        _event = values.get("event")
        _uid   = values.get("uid")

        _values = {
            "event": _event,
            "inst_id": values.get("inst_id"),
            "value": values.get("value")
        }

        if _event == None:
            return None
        # broadcast data to clients
        ws = WSConnections.getInstance()
        ws.send_data("message", _values, uid=_uid)

    def dw_response(self, flag, values):
        _uid   = values.get("uid")
        _values = {
            "event": values.get("event"),
            "hash": values.get("hash"),
            "result": values.get("result"),
        }

        if values.get("event") == None:
            return None

        ws = WSConnections.getInstance()
        ws.send_data("message", _values, uid=_uid)
