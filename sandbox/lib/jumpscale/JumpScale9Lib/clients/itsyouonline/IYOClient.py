from js9 import j
import urllib
import requests

from JumpScale9Lib.clients.itsyouonline.generated.client import Client

TEMPLATE = """
baseurl = "https://itsyou.online/api"
application_id_ = ""
secret_ = ""
"""


# TODO:*1 FROM CLIENT import .... and put in client property
# TODO:*1 regenerate using proper goraml new file & newest generation tools ! (had to fix manually quite some issues?)

JSConfigBase = j.tools.configmanager.base_class_config


class IYOClient(JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self,
                              instance=instance,
                              data=data,
                              parent=parent,
                              template=TEMPLATE,
                              interactive=interactive)

        self.reset()
        if self.config.data['secret_'] == "" or self.config.data['secret_'] == "":
            self.configure()

    @property
    def client(self):
        if self._client is None:
            self._client = Client( base_uri=self.config.data['baseurl'])
        return self._client

    @property
    def api(self):
        if self._api is None:
            self._api = self.client.api
        return self._api

    @property
    def oauth2_client(self):
        if self._oauth2_client is None:
            self._oauth2_client = self.client.Oauth2ClientOauth_2_0  #WEIRD NAME???
        return self._oauth2_client

    @property
    def jwt(self):
        if self.config.data["application_id_"] == "":
            raise RuntimeError("Please configure your itsyou.online, do this by calling js9 "
                               "'j.tools.configmanager.configure(j.clients.itsyouonline,...)'")
        if not self._jwt:
            self._jwt = self.jwt_get()
            self.api.session.headers.update({"Authorization": 'bearer {}'.format(self.jwt)})
        return self._jwt

    def reset(self):
        self._jwt = None
        self._client = None
        self._api = None
        self._oauth2_client = None

    def jwt_get(self, validity=None, refreshable=False, scope=None):
        """
        Get a a JSON Web token for an ItsYou.online organization or user.

        Args:
            validity: time in seconds after which the JWT will become invalid; defaults to 3600
            refreshable (True/False): If true the JWT can be refreshed; defaults to False
            scope: defaults to None
            base_url: base url of the ItsYou.online service; defaults to https://itsyou.online
        """

        base_url = self.config.data["baseurl"]

        params = {
            'grant_type': 'client_credentials',
            'client_id': self.config.data["application_id_"],
            'client_secret': self.config.data["secret_"],
            'response_type': 'id_token'
        }

        if validity:
            params["validity"] = validity

        if refreshable:
            params["scope"] = 'offline_access'

        if scope:
            if refreshable:
                params["scope"] = params["scope"] + "," + scope
            else:
                params["scope"] = scope

        url = urllib.parse.urljoin(base_url, '/v1/oauth/access_token')
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        jwt = resp.content.decode('utf8')
        return jwt
