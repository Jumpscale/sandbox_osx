from js9 import j

JSBASE = j.application.jsbase_get_class()


class Wrappers(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)

    def sync(self, coro):
        j.logger.get('j.tools.async').warning("j.tools.async.wrappers.sync is deprecated")
        return coro
