
from js9 import j


class ZeroStorClient:

    def __init__(self, ...):
        ...

    def put(self, data, ...):

    def getFile(self, metadata):
        """
        @return the data
        """

    def putFile(self, path, ...):
        """
        params for erasurecoding or replication or...

        @return metadata as json what is needed to restore the file
        """

    def getFile(self, metadata, path):
        """
        """

    def startClient(self):
        """
        """
        # use prefab to start the client so we can connect to it using grpc

    def installClient(self):
        """
        """
        # use prefab to build/install the client for zerostor

    def testPerformance(self):

        #... do some performance test
