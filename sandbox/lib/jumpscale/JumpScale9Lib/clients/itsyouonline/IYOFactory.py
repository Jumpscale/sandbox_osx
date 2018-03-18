

from js9 import j
from .IYOClient import IYOClient
import requests

DEFAULT_BASE_URL = "https://itsyou.online/api"

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class IYOFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = 'j.clients.itsyouonline'
        self.raml_spec = "https://raw.githubusercontent.com/itsyouonline/identityserver/master/specifications/api/itsyouonline.raml"
        JSConfigBaseFactory.__init__(self, IYOClient, single_item=True)
        self._default = None

    def install(self):
        j.tools.prefab.local.runtimes.pip.install("python-jose")

    def refresh_jwt_token(self, token, validity=86400):
        headers = {'Authorization': 'bearer %s' % token}
        params = {'validity': validity}
        resp = requests.get('https://itsyou.online/v1/oauth/jwt/refresh', headers=headers, params=params)
        resp.raise_for_status()
        return resp.content.decode()

    @property
    def default(self):
        if self._default == None:
            self._default = self.get()
        return self._default

    def test(self):
        """
        do:
        js9 'j.clients.itsyouonline.test()'
        """
        # from .generated.client.PublicKey import PublicKey #WHY THIS???

        client = j.clients.itsyouonline.default

        self.logger.info(j.clients.itsyouonline.default.jwt)

        self.logger.info(client.api.organizations.GetOrganization("threefold"))

        # TODO:*1 why username???

        # Read all the API keys registered for your user
        self.logger.debug("list all API keys")
        for key in client.api.users.ListAPIKeys(username).data:
            self.logger.debug("label: %s" % key.label)
            self.logger.debug("app ID %s" % key.applicationid)

        # Create a new API key (is really a developer way though)
        from requests.exceptions import HTTPError
        try:
            key = client.api.users.AddApiKey({"label": 'test'}, username).data
            self.logger.debug("create new API key: ")
            self.logger.debug("label: %s" % key.label)
            self.logger.debug("app ID %s" % key.applicationid)
        except HTTPError as err:
            # example of how to deal with exceptions
            if err.response.status_code == 409:
                # the key with this label already exists, no need to do anything
                pass
            else:
                raise err

        key_labels = [k.label for k in client.api.users.ListAPIKeys(username).data]
        assert 'test' in key_labels

        self.logger.debug("delete api key")
        client.api.users.DeleteAPIkey('test', username)

        key_labels = [k.label for k in client.api.users.ListAPIKeys(username).data]
        assert 'test' not in key_labels
