from js9 import j
from .DocSite import DocSite
from .Def import Def

import imp
import sys
# import inspect
# import copy

JSBASE = j.application.jsbase_get_class()


def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod


if not sys.platform.startswith("darwin"):
    caddyconfig = '''
    #tcpport:8080
    $ws/ {
        root $outpath
        browse
    }

    # $ws/fm/ {
    #     filemanager / {
    #         show           $outpath
    #         allow_new      true
    #         allow_edit     true
    #         allow_commands true
    #         allow_command  git
    #         allow_command  svn
    #         allow_command  hg
    #         allow_command  ls
    #         block          dotfiles
    #     }
    # }
    '''
else:
    caddyconfig = '''

    $ws/ {
        root $outpath
        browse
    }

    '''

caddyconfig = j.data.text.strip(caddyconfig)


class DocGenerator(JSBASE):
    """
    process all markdown files in a git repo, write a summary.md file
    optionally call pdf gitbook generator to produce pdf(s)
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.docgenerator"
        JSBASE.__init__(self)
        self.__imports__ = "toml"
        self._macroPathsDone = []
        self._initOK = False
        self._macroCodepath = j.sal.fs.joinPaths(
            j.dirs.VARDIR, "docgenerator_internal", "macros.py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(
            j.dirs.VARDIR, "docgenerator_internal"))
        self._docRootPathsDone = []
        self.docsites = {}  # location in the outpath per site
        self.outpath = j.sal.fs.joinPaths(j.dirs.VARDIR, "docgenerator")
        self.gitRepos = {}
        self.defs = {}
        self.webserver = "http://localhost:8080/"
        self.ws = self.webserver.replace(
            "http://", "").replace("https://", "").replace("/", "")
        self._loaded = []
        self._macrosLoaded = []

    def gitrepo_add(self, path):
        if path not in self.gitRepos:
            gc = j.clients.git.get(path)
            self.gitRepos[path] = gc
        return self.gitRepos[path]

    def install(self, reset=False):
        """
        js9 'j.tools.docgenerator.install()'
        """
        prefab = j.tools.prefab.local
        if prefab.core.doneGet("docgenerator:installed") == False or reset:
            prefab.system.package.install('graphviz')
            if "darwin" in str(j.core.platformtype.myplatform):                
                prefab.system.package.install('hugo')
                prefab.system.package.install('caddy')
            elif "ubuntu" in str(j.core.platformtype.myplatform):
                prefab.runtimes.golang.install()
                prefab.runtimes.nodejs.phantomjs()
                prefab.system.package.install('graphviz')
                prefab.runtimes.nodejs.install()
                # Using package install will result in an old version on some machines
                # prefab.core.file_download('https://github.com/gohugoio/hugo/releases/download/v0.26/hugo_0.26_Linux-64bit.tar.gz')
                # prefab.core.file_expand('$TMPDIR/hugo_0.26_Linux-64bit.tar.gz')
                # prefab.core.file_copy('$TMPDIR/hugo_0.26_Linux-64bit/hugo', '/usr/bin/')
                # go get github.com/kardianos/govendor
                # govendor get github.com/gohugoio/hugo
                # go install github.com/gohugoio/hugo
                prefab.core.run("go get -u -v github.com/gohugoio/hugo")
                prefab.web.caddy.build()
                prefab.core.run("npm install -g mermaid", profile=True)
                prefab.web.caddy.configure()
                prefab.core.doneSet("docgenerator:installed")

            # prefab.runtimes.pip.install(
            #     "dash,dash-renderer,dash-html-components,dash-core-components,plotly")

    def webserver_start(self):
        """
        start caddy on localhost:8080
        """
        configpath = self.caddyfile_generate()
        j.tools.prefab.local.web.caddy.start(configpath=configpath)
        self.logger.info("go to %a" % self.webserver)

    def caddyfile_generate(self):
        dest = "%s/docgenerator/caddyfile" % j.dirs.VARDIR
        j.sal.fs.createDir("%s/docgenerator" % j.dirs.VARDIR)
        out2 = caddyconfig

        C2 = """
        $ws/$name/ {
            root $vardir/docgenerator/$name/public
            #log ../access.log
        }

        """
        for key, ds in self.docsites.items():
            C3 = j.data.text.strip(C2.replace("$name", ds.name))
            out2 += C3
        out2 = out2.replace("$outpath", self.outpath)
        out2 = out2.replace("$ws", self.ws)
        out2 = out2.replace("$vardir", j.dirs.VARDIR)
        j.sal.fs.writeFile(filename=dest, contents=out2, append=False)
        return dest

    def init(self):
        if not self._initOK:
            self.install()
            j.clients.redis.core_get()
            j.sal.fs.remove(self._macroCodepath)
            # load the default macro's
            self.macros_load(
                "https://github.com/Jumpscale/docgenerator/tree/master/macros")
            self._initOK = True
        if self.webserver[-1] != "/":
            self.webserver += "/"
        self.ws = self.webserver.replace(
            "http://", "").replace("https://", "").replace("/", "")

    def macros_load(self, pathOrUrl=""):
        """
        @param pathOrUrl can be existing path or url
        e.g. https://github.com/Jumpscale/docgenerator/tree/master/examples
        """
        self.logger.info("load macros")
        path = j.clients.git.getContentPathFromURLorPath(pathOrUrl)

        if path not in self._macroPathsDone:

            if not j.sal.fs.exists(path=path):
                raise j.exceptions.Input(
                    "Cannot find path:'%s' for macro's, does it exist?" % path)

            if j.sal.fs.exists(path=self._macroCodepath):
                code = j.sal.fs.readFile(self._macroCodepath)
            else:
                code = ""

            for path0 in j.sal.fs.listFilesInDir(path, recursive=True, filter="*.py", followSymlinks=True):
                newdata = j.sal.fs.fileGetContents(path0)
                md5 = j.data.hash.md5_string(newdata)
                if md5 not in self._macrosLoaded:
                    code += newdata
                    self._macrosLoaded.append(md5)

            code = code.replace("from js9 import j", "")
            code = "from js9 import j\n\n" + code

            j.sal.fs.writeFile(self._macroCodepath, code)
            self.macros = loadmodule("macros", self._macroCodepath)
            self._macroPathsDone.append(path)

    def load(self, pathOrUrl=""):
        """

        js9 'j.tools.docgenerator.load()'

        will look for config.yaml in $source/config.yaml

        @param pathOrUrl is the location where the markdown docs are which need to be processed
            if not specified then will look for root of git repo and add docs
            source = $gitrepoRootDir/docs

            this can also be a git url e.g. https://github.com/Jumpscale/docgenerator/tree/master/examples

        """
        if pathOrUrl == "":
            pathOrUrl = j.sal.fs.getcwd()
        self.logger.info("load:%s" % pathOrUrl)
        if pathOrUrl in self._loaded:
            return
        self._loaded.append(pathOrUrl)
        self.init()
        if pathOrUrl == "":
            path = j.sal.fs.getcwd()
            path = j.clients.git.findGitPath(path)
        else:
            path = j.clients.git.getContentPathFromURLorPath(pathOrUrl)

        for docDir in j.sal.fs.listFilesInDir(path, recursive=True, filter=".docs"):
            if docDir not in self.docsites:
                self.logger.debug("found doc dir:%s" % docDir)
                ds = DocSite(path=docDir)
                self.docsites[docDir] = ds

    def generateExamples(self, start=True):
        self.load(
            pathOrUrl="https://github.com/Jumpscale/docgenerator/tree/master/examples")
        # self.load(pathOrUrl="https://github.com/Jumpscale/ays9/tree/master/docs")
        self.generate(start=start)

    def generateJSDoc(self, start=True):
        # self.load(pathOrUrl="https://github.com/Jumpscale/portal9")
        # self.load(pathOrUrl="https://github.com/Jumpscale/ays9/tree/master/docs")
        self.load(pathOrUrl="https://github.com/Jumpscale/core9/")
        self.load(pathOrUrl="https://github.com/Jumpscale/lib9")
        self.load(pathOrUrl="https://github.com/Jumpscale/prefab9")
        self.generate(start=start)

    def generate(self, url=None, start=True):
        """
        will load all info & process the pre-configured output

        js9 'j.tools.docgenerator.generate()'

        """
        if url is not None:
            self.load(pathOrUrl=url)
        if self.docsites == {}:
            self.load()
        for path, ds in self.docsites.items():
            ds.write()
        if start:
            self.webserver_start()
            self.logger.debug("TO CHECK GO TO: %s" % self.webserver)

    def git_update(self):
        if self.docsites == {}:
            self.load()
        for gc in self.gitRepos:
            gc.pull()

    def doc_get(self, name, die=True):
        for key, ds in self.docsites.items():
            if name in ds.docs:
                return ds.docs[name]
        if die:
            raise j.exceptions.Input(message="Cannot find doc with name:%s" %
                                     name, level=1, source="", tags="", msgpub="")
        else:
            return None

    def def_get(self, name):
        if name not in self.defs:
            raise RuntimeError("cannot find def:%s" % name)
        return self.defs[name]

    def docsite_get(self, name, die=True):
        name = name.lower()
        for key, ds in self.docsites.items():
            if ds.name == name:
                return ds
        if die:
            raise j.exceptions.Input(message="Cannot find docsite with name:%s" %
                                     name, level=1, source="", tags="", msgpub="")
        else:
            return None
