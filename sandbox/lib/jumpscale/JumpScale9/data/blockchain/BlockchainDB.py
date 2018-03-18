from js9 import j

JSBASE = j.application.jsbase_get_class()
class BlockchainDB(JSBASE):
    '''
    a blockchain modeled on a DB
    '''

    def __init__(self, name, db):
        JSBASE.__init__(self)
        self.name
        self.db
