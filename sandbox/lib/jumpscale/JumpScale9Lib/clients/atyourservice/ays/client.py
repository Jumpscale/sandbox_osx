from js9 import j
import requests

from .ays_service import AysService

from .Repository import Repositories
from .ActorTemplate import ActorTemplates

TEMPLATE = """
baseurl = "https://localhost:5000"
jwt_ = ""
clientid_ = ""
secret_ = ""
validity = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config
JSBASE = j.application.jsbase_get_class()


class Client(JSConfigBase):
    def __init__(self, instance, data={}, parent=None):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE)
        self._config = j.tools.configmanager._get_for_obj(
            self, instance=instance, data=data, template=TEMPLATE)

        if self.config.data['baseurl'] == '':
            self.config.configure()
        self._base_url = self.config.data['baseurl']
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._ayscl = AysService(self)
        self.templates = ActorTemplates(client=self)
        self.repositories = Repositories(self)
        if self.config.data['jwt_']:
            self._set_auth_header('Bearer {}'.format(self.config.data['jwt_']))
        if self.config.data['clientid_'] and self.config.data['secret_']:
            jwt = self._getJWT(self.config.data['clientid_'], self.config.data['secret_'], self.config.data.get('validity', None))
            self._set_auth_header('Bearer {}'.format(jwt))

    def _getJWT(self, clientID, secret, validity=3600):
        params = {
            'grant_type': 'client_credentials',
            'response_type': 'id_token',
            'client_id': clientID,
            'client_secret': secret,
            'validity': validity,
            'scope': 'offline_access'
        }
        url = 'https://itsyou.online/v1/oauth/access_token'
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        jwt = resp.content.decode('utf8')
        return jwt

    def _set_auth_header(self, val):
        ''' set authorization header value'''
        self._session.headers.update({"Authorization": val})

    def _get_headers(self, headers, content_type):
        if content_type:
            contentheader = {"Content-Type": content_type}
            if headers is None:
                headers = contentheader
            else:
                headers.update(contentheader)
        return headers

    def _handle_data(self, uri, data, headers, params, content_type, method):
        headers = self._get_headers(headers, content_type)
        if self._is_goraml_class(data):
            data = data.as_json()

        if content_type == "multipart/form-data":
            # when content type is multipart/formdata remove the content-type header
            # as requests will set this itself with correct boundary
            headers.pop('Content-Type')
            res = method(uri, files=data, headers=headers, params=params)
        elif data is None:
            res = method(uri, headers=headers, params=params)
        elif isinstance(data, str):
            res = method(uri, data=data, headers=headers, params=params)
        else:
            res = method(uri, json=data, headers=headers, params=params)
        res.raise_for_status()
        return res

    def _is_goraml_class(self, data):
        # check if a data is go-raml generated class
        # we currently only check the existence
        # of as_json method
        op = getattr(data, "as_json", None)
        if callable(op):
            return True
        return False

    def _get(self, uri, headers, params, content_type):
        headers = self._get_headers(headers, content_type)
        res = self._session.get(uri, headers=headers, params=params)
        res.raise_for_status()
        return res

    def _delete(self, uri, headers, params, content_type):
        headers = self._get_headers(headers, content_type)
        res = self._session.delete(uri, headers=headers, params=params)
        res.raise_for_status()
        return res

    def _post(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self._session.post)

    def _put(self, uri, data, headers, params, content_type):
        return self._handle_data(uri, data, headers, params, content_type, self._session.put)
