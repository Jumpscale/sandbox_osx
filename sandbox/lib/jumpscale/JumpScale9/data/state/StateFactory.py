
from js9 import j

from JumpScale9.core.State import State

JSBASE = j.application.jsbase_get_class()


class StateFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.state"
        JSBASE.__init__(self)
        self._cache = {}

    def get(self, path="/host/jumpscale9.toml"):
        """
        """
        st = State(j.tools.executorLocal,path=path)
        return st
