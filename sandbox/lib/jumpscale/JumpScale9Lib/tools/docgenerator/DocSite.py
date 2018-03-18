from js9 import j
from .Doc import Doc
import copy

import imp
import sys
# import inspect
# import copy
import pystache

DEFCONFIG = """
name = "{{NAME}}"
description = ""
depends = []
theme = "hugo-future-imperfect"
"""


def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod

JSBASE = j.application.jsbase_get_class()


class DocSite(JSBASE):
    """
    """

    def __init__(self, path=""):
        JSBASE.__init__(self)
        self.path = j.sal.fs.getDirName(path)

        gitpath = j.clients.git.findGitPath(path)

        self.git = j.tools.docgenerator.gitrepo_add(gitpath)
        self.defs = {}
        self.defaultContent = {}  # key is relative path in docsite where default content found

        data = {}
        data["webserver"] = j.tools.docgenerator.webserver
        data["NAME"] = self.git.name
        cfgpath = self.path + "config.toml"
        if not j.sal.fs.exists(cfgpath, followlinks=True):
            c = DEFCONFIG
            j.sal.fs.writeFile(cfgpath, contents=c)
        else:
            c = j.sal.fs.fileGetContents(cfgpath)
        c2 = pystache.render(c, data)
        self.config = j.data.serializer.toml.loads(c2)
        self.name = self.config["name"].strip().lower()

        # in caddy config specify the baseurl
        ws = "%s%s/" % (j.tools.docgenerator.webserver, self.name)
        self.config["baseurl"] = ws

        # need to empty again, because was used in config
        self.defaultData = {}  # key is relative path in docsite where default content found

        self.docs = {}
        self.files = {}

        self.load()

        # now go in configured git directories
        if 'depends' in self.config:
            for url in self.config['depends']:
                url = url.strip()
                path = j.clients.git.getContentPathFromURLorPath(url)
                j.tools.docgenerator.load(path)

        if 'name' not in self.config:
            raise j.exceptions.Input(message="cannot find argument 'name' in config.yaml of %s" %
                                     self.source, level=1, source="", tags="", msgpub="")

        if 'template' not in self.config:
            self.template = "https://github.com/Jumpscale/docgenerator/tree/master/templates/blog"
        else:
            self.template = self.config['template']

        self.templatePath = j.clients.git.getContentPathFromURLorPath(self.template)
        self.generatorPath = j.sal.fs.joinPaths(self.templatePath, "generator.py")

        self.templateThemePath = "%s/themes/%s" % (self.templatePath, self.config["theme"])

        # lets make sure its the outpath at this time and not the potentially changing one
        self.outpath = j.sal.fs.joinPaths(copy.copy(j.tools.docgenerator.outpath), self.name)

        self._generator = None

    def _processData(self, path):
        ext = j.sal.fs.getFileExtension(path).lower()
        if ext == "":
            # try yaml & toml
            self._processData(path + ".toml")
            self._processData(path + ".yaml")
            return

        if not j.sal.fs.exists(path):
            return {}

        if ext == "toml":
            data = j.data.serializer.toml.load(path)
        elif ext == "yaml":
            data = j.data.serializer.yaml.load(path)
        else:
            raise j.exceptions.Input(message="only toml & yaml supported", level=1, source="", tags="", msgpub="")

        if not j.data.types.dict.check(data):
            raise j.exceptions.Input(message="cannot process toml/yaml on path:%s, needs to be dict." %
                                     path, level=1, source="", tags="", msgpub="")

            # dont know why we do this? something todo probably with mustache and dots?
        keys = [str(key) for key in data.keys()]
        for key in keys:
            if key.find(".") != -1:
                data[key.replace(".", "_")] = data[key]
                data.pop(key)

        fulldirpath = j.sal.fs.getDirName(path)
        rdirpath = j.sal.fs.pathRemoveDirPart(fulldirpath, self.path)
        rdirpath = rdirpath.strip("/").strip().strip("/")
        self.defaultData[rdirpath] = data

    @property
    def url(self):
        return "%s/%s" % (j.tools.docgenerator.webserver, self.name)

    @property
    def sitepath(self):
        return "/%s/" % (self.name)

    def load(self):
        """
        walk in right order over all files which we want to potentially use (include)
        and remember their paths

        if duplicate only the first found will be used

        """
        j.sal.fs.remove(self.path + "errors.md")
        path = self.path
        if not j.sal.fs.exists(path=path):
            raise j.exceptions.NotFound("Cannot find source path in load:'%s'" % path)

        def callbackForMatchDir(path, arg):
            base = j.sal.fs.getBaseName(path)
            if base.startswith("."):
                return False

            # if base.startswith("_"):
            #     return False

            # check if we find a macro dir, if so load
            if base == "macros":
                j.tools.docgenerator.macros_load(path=path)

            if base in ["static"]:
                return False

            return True

        def callbackForMatchFile(path, arg):
            base = j.sal.fs.getBaseName(path).lower()
            # if base.startswith("_"):
            #     return False
            ext = j.sal.fs.getFileExtension(path)
            # if not ext in ["md", "yaml", "toml"]:
            #     return False
            if ext == "md" and base[:-3] in ["summary", "default"]:
                return False

            if base.startswith("_"):
                return False

            if base[:-3].lower() in ["readme"]:
                return False

            return True

        def callbackFunctionDir(path, arg):
            # will see if ther eis data.toml or data.yaml & load in data structure in this obj
            self._processData(path + "/data")
            dpath = path + "/default.md"
            if j.sal.fs.exists(dpath, followlinks=True):
                C = j.sal.fs.fileGetContents(dpath)
                rdirpath = j.sal.fs.pathRemoveDirPart(path, self.path)
                rdirpath = rdirpath.strip("/").strip().strip("/")
                self.defaultContent[rdirpath] = C
            return True

        def callbackFunctionFile(path, arg):
            ext = j.sal.fs.getFileExtension(path)
            base = j.sal.fs.getBaseName(path)
            if ext == "md":
                base = base[:-3]  # remove extension
                if base not in self.docs:
                    self.docs[base.lower()] = Doc(path, base, docsite=self)
                    # self.docsiteLast.docs[base] = self.docs[base]
            else:
                if ext in ["png", "jpg", "jpeg", "pdf", "docx", "doc", "xlsx", "xls", "ppt", "pptx", "gig", "mp4"]:
                    if base in self.files:
                        raise j.exceptions.Input(message="duplication file in %s,%s" %
                                                 (self, path), level=1, source="", tags="", msgpub="")
                    self.files[base.lower()] = path

        callbackFunctionDir(self.path, "")  # to make sure we use first data.yaml in root

        j.sal.fswalker.walkFunctional(
            self.path,
            callbackFunctionFile=callbackFunctionFile,
            callbackFunctionDir=callbackFunctionDir,
            arg="",
            callbackForMatchDir=callbackForMatchDir,
            callbackForMatchFile=callbackForMatchFile)

    def file_add(self, path):
        if not j.sal.fs.exists(path, followlinks=True):
            raise j.exceptions.Input(message="Cannot find path:%s" % path, level=1, source="", tags="", msgpub="")
        base = j.sal.fs.getBaseName(path).lower()
        self.files[base] = path

    def files_copy(self, destination="static/files"):
        dpath = j.sal.fs.joinPaths(self.outpath, destination)
        j.sal.fs.createDir(dpath)
        for name, path in self.files.items():
            j.sal.fs.copyFile(path, j.sal.fs.joinPaths(dpath, name))

    def process(self):
        for key, doc in self.docs.items():
            doc.process()

    @property
    def generator(self):
        """
        is the generation code which is in directory of the template, is called generate.py and is in root of template dir
        """
        if self._generator is None:
            self._generator = loadmodule(self.name, self.generatorPath)
        return self._generator

    def error_raise(self, errormsg, doc=None):
        if doc is not None:
            errormsg2 = "## ERROR: %s\n\n- in doc: %s\n\n%s\n" % (j.data.time.getLocalTimeHR(), doc, errormsg)
            j.sal.fs.writeFile(filename=self.path + "errors.md", contents=errormsg2, append=True)
            self.logger.error(errormsg2)
            doc.errors.append(errormsg)
        else:
            from IPython import embed
            self.logger.error("DEBUG NOW raise error")
            embed()
            raise RuntimeError("stop debug here")

    def write(self):
        j.sal.fs.removeDirTree(self.outpath)
        dest = j.sal.fs.joinPaths(self.outpath, "content")
        j.sal.fs.createDir(dest)
        # source = self.path
        # j.do.copyTree(source, dest, overwriteFiles=True, ignoredir=['.*'], ignorefiles=[
        #               "*.md", "*.toml", "_*", "*.yaml", ".*"], rsync=True, recursive=True, rsyncdelete=False)

        for key, doc in self.docs.items():
            doc.process()

        # find the defs, also process the aliases
        for key, doc in self.docs.items():
            if "tags" in doc.data:
                tags = doc.data["tags"]
                if "def" in tags:
                    name = doc.name.lower().replace("_", "").replace("-", "").replace(" ", "")
                    self.defs[name] = doc
                    if "alias" in doc.data:
                        for alias in doc.data["alias"]:
                            name = alias.lower().replace("_", "").replace("-", "").replace(" ", "")
                            self.defs[name] = doc

        for key, doc in self.docs.items():
            doc.processDefs()
            doc.write()

        self.generator.generate(self)

        if j.sal.fs.exists(j.sal.fs.joinPaths(self.path, "static"), followlinks=True):
            j.sal.fs.copyDirTree(j.sal.fs.joinPaths(self.path, "static"), j.sal.fs.joinPaths(self.outpath, "public"))

    def file_get(self, name, die=True):
        for key, val in self.files.items():
            if key.lower() == name.lower():
                return key
            ext = j.sal.fs.getFileExtension(key)
            nameLower = key[:-(len(ext) + 1)]
            if nameLower == name.lower():
                return key
        if die:
            raise j.exceptions.Input(message="Did not find file:%s in %s" %
                                     (name, self), level=1, source="", tags="", msgpub="")
        return None

    def doc_get(self, name, die=True):
        name = name.lower()
        if name in self.docs:
            return self.docs[name]
        if die:
            raise j.exceptions.Input(message="Cannot find doc with name:%s" %
                                     name, level=1, source="", tags="", msgpub="")
        else:
            return None

    def __repr__(self):
        return "docsite:%s" % ( self.path)

    __str__ = __repr__