from JumpScale9Lib.tools.async.Wrappers import Wrappers

from js9 import j
JSBASE = j.application.jsbase_get_class()

class AsyncTool(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.tools.async"
        self.wrappers = Wrappers()
        JSBASE.__init__(self)
