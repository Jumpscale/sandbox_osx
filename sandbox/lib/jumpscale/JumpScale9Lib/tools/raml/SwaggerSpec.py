
from js9 import j

JSBASE = j.application.jsbase_get_class()


class SwaggerSpec(JSBASE):

    def __init__(self, path):
        JSBASE.__init__(self)
        self.json = j.data.serializer.json.load(path)
        self.rootObjNames = [item.lstrip(
            "/") for item in self.json["paths"].keys() if item.find("{") == -1]
