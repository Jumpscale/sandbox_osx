
import struct
from js9 import j

JSBASE = j.application.jsbase_get_class()


class SerializerTime(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

    def dumps(self, obj):
        obj = struct.pack('<i', j.data.time.getTimeEpoch())
        return obj

    def loads(self, s):
        # epoch = struct.unpack('<i', s[0:2])
        return s[2:]
