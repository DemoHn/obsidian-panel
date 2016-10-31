__author__ = "Nigshoxiz"

import unittest
from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy

class SuccessHandler(MessageEventHandler):
    __prefix__ = "unit_test"

    def __init__(self):
        MessageEventHandler.__init__(self)

    def a(self, flag ,values):
        pass

    def b(self, flag, values):
        pass

    def _c(self, flag, values):
        pass

    def __invalid_method(self):
        '''
        each method should not be prefixed with "__", or it will be filtered
        :return:
        '''
        pass

class EmptyPrefixHandler(MessageEventHandler):
    def __init__(self):
        MessageEventHandler.__init__(self)

class InvalidHandler(object):
    # a valid handler must extends the parent class : MessageEventHandler
    def __init__(self):
        pass

class EventHandlerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.sender   = None

    def test_invalid_registration(self):
        self.sender = MessageQueueProxy(WS_TAG._TEST_SEND)
        self.assertRaises(ValueError, self.sender.register, InvalidHandler)

    def test_valid_registration(self):
        self.sender = MessageQueueProxy(WS_TAG._TEST_SEND)
        self.sender.register(SuccessHandler)

        exp_method_name = ['unit_test.b', 'unit_test.a','unit_test._c']
        self.assertListEqual(
            sorted(exp_method_name),
            sorted(list(self.sender.handlers.keys()))
        )

    def test_singleton(self):
        self.assertEqual(SuccessHandler(), SuccessHandler())

    def test_proxy_registration(self):
        self.sender = MessageQueueProxy(WS_TAG._TEST_SEND)
        self.sender.register(SuccessHandler)
        self.assertEqual(SuccessHandler().proxy, self.sender)

    def test_empty_prefix_registration(self):
        self.sender = MessageQueueProxy(WS_TAG._TEST_SEND)
        self.assertRaises(NotImplementedError, self.sender.register, EmptyPrefixHandler)
