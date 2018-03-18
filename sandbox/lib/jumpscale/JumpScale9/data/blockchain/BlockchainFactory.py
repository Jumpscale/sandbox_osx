from js9 import j

from BlockchainDB import BlockchainDB

JSBASE = j.application.jsbase_get_class()

class BlockchainFactory(JSBASE):
    '''
    '''

    def __init__(self):
        self.__jslocation__ = "j.data.blockchain"
        JSBASE.__init__(self)
        self.adminsecret = "admin007"
        self.port = 3302

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))

    def dbStart(self):
        cpath = self._path + "/tarantool/config.lua"
        self.db.start(configTemplatePath=cpath)

    @property
    def db(self):
        if self._db is None:
            configTemplatePath
            self._db = j.clients.tarantool.serverGet(
                name="blockchain", path="$DATADIR/tarantool/$NAME", adminsecret=self.adminsecret, port=self.port)
        return self._db

    def dbConnect(self, adminsecret="admin007"):
        self.db.connect()

    def getBaseMessage(self):
        pass
