
import os
import sys

from js9 import j

from .SwaggerSpec import *
from .RamlTools import RamlTools

JSBASE = j.application.jsbase_get_class()


class RamlToolsFactory(JSBASE):

    """
    server which generates & serves raml over gevent
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.raml"
        self._prefab = j.tools.prefab.local
        JSBASE.__init__(self)

    def _check(self):
        rc, self._goramlpath, err = j.sal.process.execute("which go-raml")
        if rc > 0:
            raise RuntimeError("Cannot find go-raml, please call 'js9_raml install'")
        self._goramlpath = self._goramlpath.strip()

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")

    def install(self, serverpips=False):
        """
        js9 'j.tools.raml.install()'
        """

        self.logger.info("goraml_install")

        # self._prefab.runtimes.nodejs.reset()
        npm_install = self._prefab.runtimes.nodejs.npm_install

        if not j.sal.process.checkInstalled("go"):
            j.tools.prefab.local.runtimes.golang.install()
            j.tools.prefab.local.runtimes.golang.goraml(reset=True)
        if not j.sal.process.checkInstalled("npm"):
            j.tools.prefab.local.runtimes.nodejs.install()

        npm_install("raml2html")
        npm_install("api-spec-converter")
        npm_install("oas-raml-converter")

        if not self._prefab.core.isMac:
            t = j.tools.code.replace_tool_get()
            t.synonymAdd(regexFind='.*node --harmony.*', replaceWith='#!/usr/bin/env node')
            t.replace_in_dir("/opt/node/bin")

        if not self._prefab.core.isMac:
            j.tools.prefab.local.system.package.install("capnproto")
        else:
            j.tools.prefab.local.system.package.install("capnp")

        # now install appropriate pips
        j.tools.prefab.local.runtimes.pip.install("autopep8")

        if serverpips:
            pips = '''
            Flask==0.10.1
            Flask-Inputs==0.2.0
            Jinja2==2.8
            MarkupSafe==0.23
            Werkzeug==0.11.4
            itsdangerous==0.24
            jsonschema==2.5.1
            six==1.10.0
            python-jose==1.3.2
            '''
            j.tools.prefab.local.runtimes.pip.install(pips)

    def upgrade(self):
        self.logger.info("goraml_ugrade")
        j.tools.prefab.local.runtimes.golang.goraml(reset=True)

    def get(self, path="", init=False):
        """
        if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml init ...

        @PARAM init, if True will remove all existing directories, so be careful !

        """
        self._check()
        if path == "":
            path = j.sal.fs.getcwd()
        else:
            j.sal.fs.createDir(path)
        if init:
            self._remove(path)
            src = "%s/baseapp/" % self._path
            j.sal.fs.copyDirTree(src, path, keepsymlinks=False,
                                 overwriteFiles=False, rsync=True, rsyncdelete=False)
            self.logger.debug("now edit main.raml in api_spec director, and run 'js9_raml generate_pyserver or other")
            return RamlTools(path)

        return RamlTools(path)

    def _remove(self, path, all=True):
        j.sal.fs.remove("%s/server" % path)
        j.sal.fs.remove("%s/client" % path)
        j.sal.fs.remove("%s/generate_client.sh" % path)
        j.sal.fs.remove("%s/generate_server.sh" % path)
        if all:
            j.sal.fs.remove("%s/api_spec" % path)
        j.sal.fs.remove("%s/generate_code.sh" % path)
        j.sal.fs.remove("%s/start_server.sh" % path)

    def test(self):
        '''
        js9 'j.tools.raml.test()'
        '''
        self.install(True)
        self.upgrade()
        path = '/tmp/ramltest'
        c = self.get(path=path, init=True)
        c.reset()

        # jwt=j.clients.itsyouonline.get().jwt
        # username =j.tools.myconfig.config.data["login_name"]

        # Test Flask Server
        self.logger.info('generate python server')
        c.server_python_generate(kind='flask')
        tmux = j.tools.prefab.local.system.processmanager.get('tmux')
        cmd = 'cd %s/server; python3 app.py' % path
        tmux.ensure('ramltest_python_server', cmd)

        self.logger.info('generate python requests client')
        # load generated client
        c.client_python_generate(kind='requests', unmarshall_response=False)  # if unmarshall is true, the client will
        # fail because the server return empty payload because we are testing an unimplemented server

        sys.path.append('/tmp/ramltest/')

        self.logger.info('test generated client')
        from client import Client
        cl = Client('http://localhost:5000')

        self.logger.info('test generate python server with generated python client')

        cl.user.getUser(id='1')
        r = cl.user.getUser(id='1')
        assert r.json() == {}
        assert r.status_code == 200
        tmux.stop('ramltest_python_server')

        j.sal.process.killProcessByPort(5000)  # For some reason after stopping the tmux, there is an orphan process
        # running on 5000

        # Test Gevent Server
        self.logger.info("generate python server")
        c.server_python_generate(kind='gevent')
        cmd = 'cd %s/server; python3 app.py' % path
        tmux.ensure('ramltest_gevent_server', cmd)

        self.logger.info('generate python gevent client')
        # load generated client
        c.client_python_generate(kind='gevent', unmarshall_response=False)  # if unmarshall is true, the client will
        # fail because the server return empty payload because we are testing an unimplemented server

        self.logger.info('test generated client')
        from client import Client
        cl = Client('http://localhost:5000')

        self.logger.info('test generate python server with generated python client')

        r = cl.user.getUser(id='1')
        assert r.json() == {}
        assert r.status_code == 200
        tmux.stop('ramltest_gevent_server')

        # TODO:*1 should test the api docs: http://localhost:5000/apidocs/index.html?raml=api.raml, just to see they are there

        # TODO:*1 get SPORE client, and do test from SPORE client

        # TODO: fix support for golang
        # doesn't work now cause go code needs to be in GOPATH
        # to build

        # self.logger.info("generate golang server")
        # c.server_go_generate()
        # cmd = 'cd %s/server; go run main.go' % path
        # tmux.ensure('ramltest_golang_server', cmd)
        # self.logger.info("test generate golang server with generated python client")
        # cl.api.users.ListAPIKeys(username)
        # tmux.stop('ramltest_golang_server')

        # self.logger.info("generate lua server")
        # c.server_go_generate()
        # tmux.ensure('ramltest_golang_server', cmd)
        # self.logger.info("test generate lua server with generated python client")
        # cl.api.users.ListAPIKeys(username)
        # tmux.stop('ramltest_golang_server')

        # raise RuntimeError("need to implement all todo's")
