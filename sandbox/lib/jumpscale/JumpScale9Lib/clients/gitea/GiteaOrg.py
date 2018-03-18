from js9 import j
from .GiteaRepo import GiteaRepo

default_labels = [
    {'color': '#e11d21', 'name': 'priority_critical'},
    {'color': '#f6c6c7', 'name': 'priority_major'},
    {'color': '#f6c6c7', 'name': 'priority_minor'},
    {'color': '#d4c5f9', 'name': 'process_duplicate'},
    {'color': '#d4c5f9', 'name': 'process_wontfix'},
    {'color': '#bfe5bf', 'name': 'state_inprogress'},
    {'color': '#bfe5bf', 'name': 'state_question'},
    {'color': '#bfe5bf', 'name': 'state_verification'},
    {'color': '#fef2c0', 'name': 'type_bug'},
    {'color': '#fef2c0', 'name': 'type_task'},
    {'color': '#fef2c0', 'name': 'type_story'},
    {'color': '#fef2c0', 'name': 'type_feature'},
    {'color': '#fef2c0', 'name': 'type_question'}
]

JSBASE = j.application.jsbase_get_class()


class GiteaOrg(JSBASE):

    def __init__(self, client, name):
        JSBASE.__init__(self)
        self.name = name
        self.id = client.orgs_currentuser_list()[name]
        self.client = client
        self.api = self.client.api.orgs

    def labels_default_get(self):
        return default_labels

    def _repos_get(self, refresh=False):
        def do():
            res = {}
            for item in self.client.api.orgs.orgListRepos(self.name)[0]:
                res[item.name] = item
            return res
        return self.cache.get("orgs", method=do, refresh=refresh, expire=60)

    def repos_list(self, refresh=False):
        res = {}
        for name, item in self._repos_get(refresh=refresh).items():
            res[name] = item.id
        return res

    def repo_get(self, name):
        self.logger.info("repo:get:%s" % name)
        if name not in self._repos_get().keys():
            raise RuntimeError("cannot find repo with name:%s in %s" % (name, self))
        data = self._repos_get()[name]
        return GiteaRepo(self, name, data)

    def repo_new(self, name):
        self.logger.info("repo:new:%s" % name)
        if name in self._repos_get().keys():
            self.logger.debug("no need to create repo on gitea, exists:%s"%name)
        self.client.api.org.createOrgRepo(data, org)#TODO:*1
        raise RuntimeError("NEED TO IMPLEMENT THIS")
        return GiteaRepo(self, name, data)

    def labels_milestones_add(self, labels=default_labels, remove_old=False):
        """
        If a label with the same name exists on a repo, it won't be added.

        :param labels: a list of labels  ex: [{'color': '#fef2c0', 'name': 'state_blocked'}]

        goes over all repo's in this org

        """
        for repo_name in self.repos_list():
            repo = self.repo_get(repo_name)

            repo.milestones_add(remove_old=remove_old)
            repo.labels_add(remove_old=remove_old)

    def __repr__(self):
        return "org:%s" % self.name

    __str__ = __repr__
