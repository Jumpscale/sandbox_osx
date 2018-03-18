from js9 import j

from pprint import pprint as print
from .OVCClient import OVCClient

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class OVCClientFactory(JSConfigBaseFactory):
    """
    get method:
        this will return a client

        in data need:
            address = ""
            port = 443
            jwt_ = ""

        jwt can be gotten from: j.clients.itsyouonline.default.jwt
        if not filled in will bet done auto

    """

    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"
        self.__imports__ = "ovc"
        JSConfigBaseFactory.__init__(self, OVCClient)

    def getFromParams(self, address, location="", port=443, instance="main", ):
        """
        example address:
        - be-gen-1.demo.greenitglobe.com

        the jwt will be fetched from ' j.clients.itsyouonline.default.jwt'

        @PARAM if location not specified will check which one is on environment and if only one use that one

        """

        data = {}
        data["address"] = address
        data["port"] = int(port)
        data["location"] = location

        return self.get(instance=instance, data=data)

    def test(self):
        """
        js9 'j.clients.openvcloud.test()'
        """
        self.logger_enable()
        cl = j.clients.openvcloud.getFromParams("be-gen-1.demo.greenitglobe.com")
        self.logger.info(cl.config)

        self.logger.info("locations")
        self.logger.info(cl.locations)

        self.logger.info("images")
        self.logger.info(cl.get_available_images())
