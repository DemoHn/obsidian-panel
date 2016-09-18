import socket
import logging
import struct

class MCSocket(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def _pack_variant(self, data):
        """ Pack the var int """
        ordinal = b''

        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break
        return ordinal

    def _pack_data(self, data):
        if type(data) is str:
            _data = data.encode("utf-8")
            return self._pack_variant(len(_data)) + _data
        elif type(data) is int:
            return struct.pack("H", data)
        elif type(data) is float:
            return struct.pack("L", int(data))
        else:
            return data

    def connect(self, port, ip="127.0.0.1"):
        address = (ip, port)
        self.sock.connect(address)
        self.sock.setblocking(0)

    def send_data(self, *args):
        _data = b''

        for arg in args:
            _data += self._pack_data(arg)
        self.sock.send(self._pack_variant(len(_data)) + _data)
