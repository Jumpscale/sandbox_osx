
from js9 import j
from JumpScale9Lib.clients.zerorobot.client import Client

JSConfigClientBase = j.tools.configmanager.base_class_config


_template = """
url = "http://localhost:6600"
"""


class ZeroRobotClient(JSConfigClientBase):

    def __init__(self, instance="main", data={}, parent=None, template=None, ui=None, interactive=True):
        """
        @param instance: instance name
        @param data: configuration data. if specified will update the configuration with it
        @param parent: used by configmanager, you probably don't need to deal with it manually
        """
        data = data or {}
        super().__init__(instance=instance, data=data, parent=parent, template=_template, ui=ui, interactive=interactive)
        self._api = None

    @property
    def api(self):
        """
        regroup all of the method to talk to the ZeroRobot API
        """
        if self._api is None:
            self._api = Client(base_uri=self.config.data["url"])
        return self._api
