import unittest
from app.tools.mq_proxy import MessageQueueProxy, WS_TAG, MessageEventHandler
import multiprocessing
import time
import traceback

from threading import Event
from tests.async_test import AsyncTestCase

class MessageQueueProxyTest(AsyncTestCase):
    def unlock(self, flag, values):
        _assert_values = {"a":"b"}
        try:
            if flag == "hello_world":
                self.assertDictEqual(_assert_values, values)
        except:
            traceback.print_exc()
            self.stop()
            return None

        self.stop()
    def __init__(self, *args, **kwargs):
        AsyncTestCase.__init__(self, *args, **kwargs)
        self.sender   = None
        self.receiver = None
        self.process  = None

        def _setup_process():
            self.receiver = MessageQueueProxy(WS_TAG._TEST_RECV)
            self.receiver.register(self.ReceiverHandler)
            self.receiver.listen(background=False)

        self.process = multiprocessing.Process(target=_setup_process)
        self.process.start()

    # nested handler
    class ReceiverHandler(MessageEventHandler):
        __prefix__ = "test"

        def __init__(self):
            MessageEventHandler.__init__(self)

        def echo(self, flag, values):
            # send back the same data
            self.proxy.send(flag, "test.echo_back", values, WS_TAG._TEST_SEND)

    def setUp(self):
        super(MessageQueueProxyTest, self).setUp()

        self.sender = MessageQueueProxy(WS_TAG._TEST_SEND)
        self.sender._register_handler("test.echo_back", self.unlock)
        #self.sender.register(self.SenderHandler)
        self.sender.listen(background=True)

    def tearDown(self):
        super(MessageQueueProxyTest, self).tearDown()
        self.process.terminate()
        self.sender.terminate()


    def test_send(self):
        self.sender.send("hello_world", "test.echo", {"a": "b"}, WS_TAG._TEST_RECV)
        self.wait()

        #self._done = Event()
        #self.sender.send("hello_world", "test.echo", {"b": "c"}, WS_TAG._TEST_RECV)
        #self.wait()



