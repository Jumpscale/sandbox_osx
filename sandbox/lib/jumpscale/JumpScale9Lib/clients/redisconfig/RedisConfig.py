from js9 import j

TEMPLATE = """
addr = "127.0.0.1"
port = 6379
password_ = ""
ardb_patch = false
unixsocket = ""
set_patch = false
"""

JSConfigBase = j.tools.configmanager.base_class_config


class RedisConfig(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, interactive=interactive)
        self._redis = None

    @property
    def redis(self):
        if self._redis is None:
            d = self.config.data
            addr = d["addr"]
            port = d["port"]
            password = d["password_"]
            unixsocket = d["unixsocket"]
            ardb_patch = d["ardb_patch"]
            set_patch = d["set_patch"]
            if unixsocket == "":
                unixsocket = None
            self._redis = j.clients.redis.get(
                ipaddr=addr, port=port, password=password, unixsocket=unixsocket, ardb_patch=ardb_patch, set_patch=set_patch)
        return self._redis

    def __str__(self):
        return "redis:%-14s %-25s:%-4s" % (self.instance, self.config.data["addr"],  self.config.data["port"])

    __repr__ = __str__
