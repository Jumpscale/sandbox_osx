from .ZeroHubClient import ZeroHubClient
from js9 import j

JSConfigFactory = j.tools.configmanager.base_class_configs
class ZeroHubFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.zerohub"
        JSConfigFactory.__init__(self, ZeroHubClient)
