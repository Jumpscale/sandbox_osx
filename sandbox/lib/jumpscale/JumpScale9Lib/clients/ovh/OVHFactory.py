from js9 import j

from .OVHClient import OVHClient

JSConfigBase = j.tools.configmanager.base_class_configs


class OVHFactory(JSConfigBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.ovh"
        self.__imports__ = "ovh"
        JSConfigBase.__init__(self, OVHClient)

    def install(self):
        p = j.tools.prefab.local
        p.runtimes.pip.install("ovh")

    def get_manual(self, instance, appkey, appsecret, consumerkey="", endpoint='soyoustart-eu', ipxeBase="https://bootstrap.gig.tech/ipxe/master"):
        """

        @PARAM instance is the name of this client

        Visit https://eu.api.soyoustart.com/createToken/

        IMPORTANT:
        for rights add get,post,put & delete rights
        for each of them put /*
        this will make sure you have all rights on all methods recursive

        to get your credentials

        endpoints:
            ovh-eu for OVH Europe API
            ovh-ca for OVH North-America API
            soyoustart-eu for So you Start Europe API
            soyoustart-ca for So you Start North America API
            kimsufi-eu for Kimsufi Europe API
            kimsufi-ca for Kimsufi North America API
            runabove-ca for RunAbove API

        """
        data = {}
        data["appkey_"] = appkey
        data["appsecret_"] = appsecret
        data["consumerkey_"] = consumerkey
        data["endpoint"] = endpoint
        data["ipxeBase"] = ipxeBase

        return self.get(instance=instance, data=data)

    # def node_get(self,instance=""):
    #     cl=j.clients.ovh.client_get(instance=instance)
    #     cl.serverInstall(name="", installationTemplate="ubuntu1704-server_64", sshKeyName="ovh",
    # useDistribKernel=True, noRaid=True, hostname="", wait=True)

    def test(self):
        """
        do:
        js9 'j.clients.ovh.test()'
        """
        client = self.get()
        self.logger.debug(client.serversGet())
