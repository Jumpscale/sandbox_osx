
import os
import sys

from js9 import j

from .SwaggerSpec import *
JSBASE = j.application.jsbase_get_class()


class RamlTools(JSBASE):

    def __init__(self, path):
        JSBASE.__init__(self)
        self.path = path
        self.goramlpath = j.tools.raml._goramlpath
        if not j.sal.fs.exists("%s/api_spec" % self.path):
            raise RuntimeError("Cannot find api_spec dir in %s, please use 'js9_raml init' to generate." % path)

    def _get_kind(self, supported_kinds, kind):
        try:
            kind = supported_kinds[kind]
        except KeyError:
            raise ValueError("Kind of server/client not supported : %s" % kind)
        return kind

    def reset(self):
        j.tools.raml._remove(self.path, all=False)

    def specs_get(self, giturl):
        """
        e.g. https://github.com/itsyouonline/identityserver/tree/master/specifications/api
        """
        specpath_downloaded = j.clients.git.getContentPathFromURLorPath(giturl)
        specpath = "%s/api_spec" % self.path
        j.sal.fs.remove(specpath)
        j.sal.fs.copyDirTree(specpath_downloaded, specpath)
        sfiles = j.sal.fs.listFilesInDir(specpath, filter='*.raml')
        sfile = "%s/main.raml" % specpath
        if len(sfiles) == 1:
            # check is main.raml, if not rename
            sfile = "%s/main.raml" % specpath
            if not j.sal.fs.exists(sfile):
                self.logger.debug("could not find main raml, file will rename")
                j.sal.fs.renameFile(sfiles[0], sfile)
        else:
            if not j.sal.fs.exists(sfile):
                raise RuntimeError("could not find specfile:%s" % sfile)

    def _get_cmd(self, no_apidocs=False, no_main=False, lib_root_urls='', import_path='', api_file_per_method=False,
                 kind='', package='', unmarshall_response=False):
        cmd = "cd {path};mkdir -p {type};cd api_spec;{goraml} {type} --language {lang} \
                    --dir ../{type}/ --ramlfile main.raml"
        if no_apidocs:
            cmd += ' --no-apidocs'
        if no_main:
            cmd += ' --no-main'
        if lib_root_urls:
            cmd += ' --lib-root-urls {urls}'
        if import_path:
            cmd += ' --import-path {import_path}'
        if api_file_per_method:
            cmd += ' --api-file-per-method'
        if package:
            cmd += ' --package {package}'
        if kind:
            cmd += ' --kind {kind}'
        if unmarshall_response:
            cmd += ' --python-unmarshall-response'

        return cmd

    def _client_generate(self, reset=False, cmd='', doc=True):
        if reset:
            self.reset()

        j.sal.process.executeInteractive(cmd)

        if doc:
            cmd = "cd %s;rm -rf htmldoc;mkdir -p htmldoc; \
            cd ../api_spec; \
            raml2html -i main.raml -o api.html&& mv api.html ../client/htmldoc/api.html -v" % j.sal.fs.joinPaths(self.path, 'client')
            j.sal.process.executeInteractive(cmd)

        # TODO: test and re-enable
        # cmd = "cd %s;cd api_spec;oas-raml-converter --from RAML --to OAS20 main.raml > ../generated/swagger_api.json" % self.path
        # j.sal.process.execute(cmd)

    def _server_generate(self, reset=False, cmd=''):
        if reset:
            self.reset()

        j.sal.process.execute(cmd)

        # TODO: re-enable when generation of swagger is fixed
        # spec = SwaggerSpec("%s/generated/swagger_api.json" % self.path)

    def client_python_generate(self, reset=False, kind='requests', unmarshall_response=True, doc=True):
        """
        generate the client from self.path specified, if not specified will be current dir

        js9_raml generate_pyclient
        """
        supported_map = {
            'gevent': 'gevent-requests',
            'requests': 'requests',
            'aiohttp': 'aiohttp',
        }
        kind = self._get_kind(supported_map, kind)

        cmd = self._get_cmd(kind=kind, unmarshall_response=unmarshall_response)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, kind=kind, lang='python', type='client')

        self._client_generate(reset=reset, cmd=cmd, doc=doc)

    def client_go_generate(self, reset=False, package='client', import_path='', lib_root_urls=''):
        """
        generate the client from self.path specified, if not specified will be current dir

        js9_raml generate_goclient
        """

        cmd = self._get_cmd(package=package, import_path=import_path, lib_root_urls=lib_root_urls)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='go',
                         import_path=import_path, urls=lib_root_urls, package=package, type='client')
        self._client_generate(reset=reset, cmd=cmd)

    def client_nim_generate(self, reset=False):
        """
        generate the client from self.path specified, if not specified will be current dir

        js9_raml generate_goclient
        """
        cmd = self._get_cmd()
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='nim', type='client')
        self._client_generate(reset=reset, cmd=cmd)

    def server_python_generate(self, reset=False, kind='gevent',
                               no_apidocs=False, no_main=False, lib_root_urls=''):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        supported_map = {
            'gevent': 'gevent-flask',
            'flask': 'flask',
            'sanic': 'sanic',
        }
        kind = self._get_kind(supported_map, kind)
        cmd = self._get_cmd(kind=kind, no_apidocs=no_apidocs, no_main=no_main, lib_root_urls=lib_root_urls)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='python',
                         kind=kind, urls=lib_root_urls, type='server')

        self._server_generate(reset=reset, cmd=cmd)

    def server_go_generate(self, reset=False, package='server', no_main=False, no_apidocs=False, import_path='',
                           lib_root_urls='', api_file_per_method=True):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        cmd = self._get_cmd(package=package, no_apidocs=no_apidocs, no_main=no_main, import_path=import_path,
                            lib_root_urls=lib_root_urls, api_file_per_method=api_file_per_method)
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='go', package=package,
                         import_path=import_path, urls=lib_root_urls, type='server')

        self._server_generate(reset=reset, cmd=cmd)

    def server_lua_generate(self, reset=False):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        cmd = self._get_cmd()
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='tarantool', type='server')
        self._server_generate(reset=reset, cmd=cmd)

    def server_nim_generate(self, reset=False):
        """
        generate the site from self.path specified, if not specified will be current dir

        can call this command line too (be in self.path where you want to work):
        js9_raml generate
        """
        cmd = self._get_cmd()
        cmd = cmd.format(path=self.path, goraml=self.goramlpath, lang='nim', type='server')
        self._server_generate(reset=reset, cmd=cmd)

    def server(self):
        cmd = "cd %s;sh start_server.sh" % self.path
        j.sal.process.executeInteractive(cmd)
