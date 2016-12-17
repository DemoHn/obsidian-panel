__author__ = "Nigshoxiz"

import unittest

# sync tests
test_modules = [
    #'proxy.test_event_handler',
    #'proxy.test_mq_proxy'
    'test_hello'
]

suite = unittest.TestSuite()

for t in test_modules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite)
    #import proxy.test_event_handler