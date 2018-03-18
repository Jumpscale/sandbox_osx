from .ZeroStorClient import ZeroStorClient
from js9 import j

JSBASE = j.application.jsbase_get_class()


class ZeroStorFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.clients.zerostor"
        self.__imports__ = "requests"
        JSBASE.__init__(self)

    def getClient(self):
        """
        # Getting client via accesstoken


        """
        return ZeroStorClient
