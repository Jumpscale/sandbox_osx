from js9 import j

# IMPORTANT
# use functionality in j.clients.ssh to deal with SSH-Agent & getting key info, improve if required
# use j.data.nacl for underlying encryption/decryption/signing when possible
JSBASE = j.application.jsbase_get_class()

class EncryptionFactory(JSBASE):
    """
    EncryptionFactory provides the means to sign, encrypt data using NACL
    """

    def __init__(self):
        self.__jslocation__ = "j.data.encryption"
        JSBASE.__init__(self)

    def sign_short(self, data, keyname, keypath=None):
        """
        Sign data using NACL
            :param data: data to be signed
            :param keyname: filename that contains the private key to encrypt and sign the data
            :param keypath: path of dir of the key file, if None it'll fall back to ~/.ssh
            @return: tuple of signed data and signature used in verification
        """

        encrypted = j.data.nacl.encrypt(data=data,
                                        keyname=keyname,
                                        keypath=keypath)
        signed, signature = j.data.nacl.sign(encrypted)
        return signed, signature

    def verify_short(self, data, signature, keyname, keypath):
        """
        Verify data using signature
            :param data: signed data to be verified using signature
            :param signature: signature that was used to signed the data
            :param keyname: filename that contains the private key to decrypt and sign the data
            :param keypath: path of dir of the key file, if None it'll fall back to ~/.ssh
            @return original data
        """

        verified_data = j.data.nacl.verify(data, signature)
        return j.data.nacl.decrypt(data=verified_data,
                                   keyname=keyname,
                                   keypath=keypath)
