from js9 import j

from .NACLClient import NACLClient



JSBASE = j.application.jsbase_get_class()

class NACLClientFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.nacl"
        self._default = None

    def get(self, name="key", secret="", sshkeyname=""):
        """
        if more than 1 will match ourid (generated from sshagent)
        if path not specified then is ~/.secrets
        """
        return NACLClient(name, secret, sshkeyname=j.tools.configmanager.keyname)

    @property
    def default(self):
        if self._default is None:
            self._default = self.get()
        return self._default

    def test(self):
        """
        js9 'j.data.nacl.test()'
        """

        cl = self.default  # get's the default location & generate's keys

        data = b"something"
        r = cl.sign(data)

        assert cl.verify(data,r) == True
        assert cl.verify(b"a",r) == False

        pubsignkey32 = cl.signingkey_pub.encode()

        assert cl.verify(data,r,pubsignkey32) == True

        a = cl.encryptSymmetric("something")
        b = cl.decryptSymmetric(a)

        assert b == b"something"

        a = cl.encryptSymmetric("something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = cl.encryptSymmetric("something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = cl.encryptSymmetric(b"something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        # now with hex
        a = cl.encryptSymmetric(b"something", "qwerty", hex=True)
        b = cl.decryptSymmetric(a, b"qwerty", hex=True)
        assert b == b"something"

        a = cl.encrypt(b"something")
        b = cl.decrypt(a)

        assert b == b"something"

        a = cl.encrypt("something")  # non binary start
        b = cl.decrypt(a)

        # now with hex
        a = cl.encrypt("something", hex=True)  # non binary start
        b = cl.decrypt(a, hex=True)
        assert b == b"something"

        self.logger.info("TEST OK")

    def test_perf(self):
        """
        js9 'j.data.nacl.test_perf()'
        """

        cl = self.default  # get's the default location & generate's keys
        data = b"something"

        nr=10000
        j.tools.timer.start("signing")
        for i in range(nr):  
            p = str(i).encode()      
            r = cl.sign(data+p)
        j.tools.timer.stop(i)
        
        nr=10000
        j.tools.timer.start("encode and verify")
        for i in range(nr):  
            p = str(i).encode()
            r = cl.sign(data+p)      
            assert cl.verify(data+p,r) == True
        j.tools.timer.stop(i)        

        nr=10000
        data2=data*20
        j.tools.timer.start("encryption/decryption assymetric")
        for i in range(nr):  
            a = cl.encrypt(data2)
            b = cl.decrypt(a)
            assert data2==b
        j.tools.timer.stop(i)  


        nr=40000
        secret = b"something111"
        data2=data*20
        j.tools.timer.start("encryption/decryption symmetric")
        for i in range(nr):  
            a = cl.encryptSymmetric(data2,secret=secret)
            b = cl.decryptSymmetric(a,secret=secret)
            assert data2==b
        j.tools.timer.stop(i)  

