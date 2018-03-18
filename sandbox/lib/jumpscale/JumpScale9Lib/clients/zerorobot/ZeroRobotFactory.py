import os

from js9 import j
from JumpScale9Lib.clients.zerorobot.ZeroRobotClient import ZeroRobotClient

JSConfigFactoryBase = j.tools.configmanager.base_class_configs


class ZeroRobotFactory(JSConfigFactoryBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zrobot"
        super().__init__(child_class=ZeroRobotClient)

    def generate(self):
        """
        generate the client out of the raml specs
        """
        path = j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")
        c = j.tools.raml.get(path)
        # c.specs_get('https://github.com/Jumpscale/0-robot/blob/master/raml')
        c.client_python_generate()
