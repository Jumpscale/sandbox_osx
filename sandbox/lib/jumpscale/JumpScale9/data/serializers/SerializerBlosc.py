import blosc
from .SerializerBase import *
from js9 import j

class SerializerBlosc(SerializerBase):

    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj):
        return blosc.compress(obj, typesize=8)

    def loads(self, s):
        return blosc.decompress(s)
