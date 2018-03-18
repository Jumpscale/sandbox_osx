from js9 import j
from .energyswitch.client import RackSal

JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
username = ""
password_ = ""
hostname = "127.0.0.1"
port = 8080
"""


class RacktivityFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.racktivity"
        JSConfigFactory.__init__(self, RacktivityClient)


class RacktivityClient(JSConfigClient, RackSal):

    def __init__(self, instance, data={}, parent=None):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE)
        c = self.config.data
        RackSal.__init__(self, c['username'], c['password_'], c['hostname'], c['port'], rtf=None, moduleinfo=None)
