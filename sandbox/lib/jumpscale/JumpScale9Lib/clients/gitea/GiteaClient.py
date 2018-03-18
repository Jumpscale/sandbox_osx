from js9 import j

from .GiteaOrg import GiteaOrg

from JumpScale9Lib.clients.gitea.client import Client


TEMPLATE = """
url = ""
gitea_token_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config
JSBASE = j.application.jsbase_get_class()


class GiteaClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None,interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE,interactive=interactive)
        self._api = None

    def config_check(self):
        """
        check the configuration if not what you want the class will barf & show you where it went wrong
        """

        if self.config.data["url"] == "" or self.config.data["gitea_token_"] == "":
            return "url and gitea_token_ are not properly configured, cannot be empty"

        base_uri = self.config.data["url"]
        if "/api" not in base_uri:
            self.config.data_set("url", "%s/api/v1" % base_uri)
            self.config.save()

        # TODO:*1 need to do more checks that url is properly formated

    @property
    def api(self):
        if not self._api:
            self._api = Client(base_uri=self.config.data["url"])
            self._api.security_schemes.passthrough_client_token.set_authorization_header(
                'token {}'.format(self.config.data["gitea_token_"]))
        return self._api

    def orgs_currentuser_list(self, refresh=False):
        """
        returns [(id,name)]
        """
        def do():
            res = {}
            for item in self.api.user.orgListCurrentUserOrgs()[0]:
                res[item.username] = item.id
            return res
        return self.cache.get("orgs", method=do, refresh=refresh, expire=60)

    def org_get(self, name):
        self.logger.info("org:get:%s" % name)
        if name not in self.orgs_currentuser_list().keys():
            raise RuntimeError("Could not find %s in orgs on gitea" % name)
        return GiteaOrg(self, name)

    def labels_milestones_set(self, orgname="*", reponame="*", remove_old=False):
        """
        * means all in the selection

        @PARAM remove_old if True will select labels/milestones which are old & need to be removed

        """
        self.logger.info("labels_milestones_set:%s:%s" % (orgname, reponame))
        if orgname == "*":
            for orgname0 in self.orgs_currentuser_list():
                self.labels_milestones_set(orgname=orgname0, reponame=reponame, remove_old=remove_old)
            return

        org = self.org_get(orgname)

        if reponame == "*":
            for reponame0 in org.repos_list():
                # self.logger.debug(org.repos_list())
                # self.logger.debug("reponame0:%s"%reponame0)
                self.labels_milestones_set(orgname=orgname, reponame=reponame0, remove_old=remove_old)
            return

        repo = org.repo_get(reponame)
        repo.labels_add(remove_old=remove_old)
        repo.milestones_add(remove_old=remove_old)

    def __repr__(self):
        return "gitea client"

    __str__ = __repr__
