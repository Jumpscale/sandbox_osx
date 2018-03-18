from js9 import j


TEMPLATE = """
api_key_ = ""
private_key_ = ""
"""

JSConfigClient = j.tools.configmanager.base_class_config
JSConfigFactory = j.tools.configmanager.base_class_configs


class KrakenClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE)
        import krakenex
        from pykrakenapi import KrakenAPI

        kraken_api = krakenex.API()
        kraken_api.key=self.config.data["api_key_"]
        kraken_api.secret=self.config.data["private_key_"]
        self.api = KrakenAPI(kraken_api)

    def test(self):

        k = self.api
        self.logger.debug ("open orders")
        self.logger.debug(k.get_open_orders())

        self.logger.debug("get account balance")
        self.logger.debug(k.get_account_balance())

class Kraken(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = 'j.clients.kraken'
        JSConfigFactory.__init__(self, KrakenClient)

    def install(self,reset=False):
        j.tools.prefab.local.runtimes.pip.install("pykrakenapi",reset=reset)
        j.tools.prefab.local.runtimes.pip.install("krakenex",reset=reset)

