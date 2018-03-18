from js9 import j

try:
    import ujson as json
except BaseException:
    import json
from .SerializerBase import SerializerBase


class SerializerUJson(SerializerBase):

    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj, sort_keys=False, indent=False):
        return json.dumps(obj, ensure_ascii=False, sort_keys=sort_keys, indent=indent)

    def loads(self, s):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return json.loads(s)
