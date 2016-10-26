class MessageEventHandler(object):
    __prefix__ = None

    def __init__(self):
        if self.__class__.__prefix__ == None:
            raise Exception("Prefix not set!")