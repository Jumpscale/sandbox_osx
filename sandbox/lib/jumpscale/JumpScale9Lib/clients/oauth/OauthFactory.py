import os


from js9 import j
from .OauthInstance import OauthClient

JSConfigFactory = j.tools.configmanager.base_class_configs


class OauthFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.oauth"
        JSConfigFactory.__init__(self, OauthClient)
