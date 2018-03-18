from js9 import j
from .PortalClient import PortalClient

JSConfigBaseFactory = j.tools.configmanager.base_class_configs
class PortalClientFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.portal"
        self._portalClients = {}
        JSConfigBaseFactory.__init__(self, PortalClient)
