from js9 import j
# import os
# import copy

JSBASE = j.application.jsbase_get_class()


class Config(JSBASE):

    def __init__(self, instance="main", location=None, template={}, data={}):
        """
        jsclient_object is e.g. j.clients.packet.net
        """

        JSBASE.__init__(self)

        self.location = location
        self.instance = instance
        self._template = template
        if self.instance is None:
            raise RuntimeError("instance cannot be None")

        self.reset()
        if not j.sal.fs.exists(self.path):
            j.sal.fs.createDir(j.sal.fs.getDirName(self.path))            
            self.new = True
            dataOnFS = {}
        else:
            self.load()
            # this is data on disk, because exists, should already apply to template
            # without decryption so needs to go to self._data
            dataOnFS = self.data  # now decrypt

        # make sure template has been applied !
        data2, error = j.data.serializer.toml.merge(tomlsource=self.template, tomlupdate=dataOnFS, listunique=True)

        if data != {}:
            # update with data given
            data, error = j.data.serializer.toml.merge(tomlsource=data2, tomlupdate=data, listunique=True)
            self.data = data
        else:
            # now put the data into the object (encryption)
            self.data = data2

        # do the fancydump to make sure we really look at differences
        if j.data.serializer.toml.fancydumps(self.data) != j.data.serializer.toml.fancydumps(dataOnFS):
            self.logger.debug("change of data in config, need to save")
            self.logger.debug("OLD\n%s" % j.data.serializer.toml.fancydumps(dataOnFS))
            self.logger.debug("NEW\n%s" % j.data.serializer.toml.fancydumps(self.data))
            self.save()

    def reset(self):
        self._data = {}
        self.loaded = False
        self._path = None
        self._nacl = None
        self.new = False

    @property
    def path(self):
        self.logger.debug("init getpath:%s" % self._path)
        if not self._path:
            self._path = j.sal.fs.joinPaths(j.tools.configmanager.path, self.location, self.instance + '.toml')
            self.logger.debug("getpath:%s" % self._path)
        return self._path

    @property
    def nacl(self):
        if not self._nacl:
            if j.tools.configmanager.keyname:
                self._nacl = j.data.nacl.get(sshkeyname=j.tools.configmanager.keyname)
            else:
                self._nacl = j.data.nacl.get()
        return self._nacl

    def instance_set(self, instance):
        """
        will change instance name & delete data
        """
        self.instance = instance
        self.load(reset=True)

    def load(self, reset=False):
        """
        @RETURN if 1 means did not find the toml file so is new
        """
        if reset or self._data == {}:
            if not j.sal.fs.exists(self.path):
                raise RuntimeError("should exist at this point")
            else:
                content = j.sal.fs.fileGetContents(self.path)
                self._data = j.data.serializer.toml.loads(content)
            for key, val in self.template.items():
                ttype = j.data.types.type_detect(self.template[key])
                if ttype.BASETYPE == "string":
                    self._data[key] = self._data[key].strip()

    def save(self):
        # at this point we have the config & can write (self._data has the encrypted pieces)
        j.sal.fs.writeFile(
            self.path, j.data.serializer.toml.fancydumps(self._data))

    def delete(self):
        j.sal.fs.remove(self.path)

    @property
    def template(self):
        if self._template is None or self._template == '':
            raise RuntimeError("self._template has to be set")
        if j.data.types.string.check(self._template):
            self._template = j.data.serializer.toml.loads(self._template)
        return self._template

    @property
    def data(self):
        res = {}
        if self._data == {}:
            self.load()
        for key, item in self._data.items():
            ttype = j.data.types.type_detect(self.template[key])
            if key.endswith("_"):
                if ttype.BASETYPE == "string":
                    if item != '' and item != '""':
                        res[key] = self.nacl.decryptSymmetric(item, hex=True).decode()
                    else:
                        res[key] = ''
                else:
                    res[key] = item
            else:
                res[key] = item
        return res

    @data.setter
    def data(self, value):
        if j.data.types.dict.check(value) is False:
            raise TypeError("value needs to be dict")

        changed = False
        for key, item in value.items():
            ch1 = self.data_set(key, item, save=False)
            changed = changed or ch1

        if changed:
            # raise RuntimeError()
            self.logger.debug("changed:\n%s" % self)
            self.save()

    def data_set(self, key, val, save=True):
        if key not in self.template:
            raise RuntimeError(
                "Cannot find key:%s in template for %s" % (key, self))

        if key not in self._data or self._data[key] != val:
            ttype = j.data.types.type_detect(self.template[key])
            if key.endswith("_"):
                if ttype.BASETYPE == "string":
                    if val != '' and val != '""':
                        val = self.nacl.encryptSymmetric(val, hex=True, salt=val)
                        if key in self._data and val == self._data[key]:
                            return False
            self._data[key] = val
            if save:
                self.save()
            return True
        else:
            return False

    @property
    def yaml(self):
        return j.data.serializer.toml.fancydumps(self._data)

    def __str__(self):
        out = "config:%s:%s\n\n" % (self.location, self.instance)
        out += j.data.text.indent(self.yaml)
        return out

    __repr__ = __str__
