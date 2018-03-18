from js9 import j

from .RedisConfig import RedisConfig


JSConfigBase = j.tools.configmanager.base_class_configs


class RedisConfigFactory(JSConfigBase):

    def __init__(self):
        if not hasattr(self, '__jslocation__'):
            self.__jslocation__ = "j.clients.redis_config"
        JSConfigBase.__init__(self, RedisConfig)
        self._tree = None

    def get_by_params(self, instance="core",ipaddr="localhost", port=6379, password="", unixsocket="", ardb_patch=False, set_patch=False):
        data = {}
        data["addr"] = ipaddr
        data["port"] = port
        data["password_"] = password
        data["unixsocket"] = unixsocket
        data["ardb_patch"] = ardb_patch
        data["set_patch"] = set_patch
        return self.get(instance=instance, data=data)

    def test(self):
        j.clients.redis.core_start()
        cl = self.get_by_params(port=6379)
        assert cl.redis.ping() == True
        