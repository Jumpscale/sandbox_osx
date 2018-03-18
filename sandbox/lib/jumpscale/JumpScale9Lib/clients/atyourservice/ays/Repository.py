import json
from requests.exceptions import HTTPError
from .ActorTemplate import ActorTemplates
from .Actor import Actors
from .Blueprint import Blueprints
from .Service import Services
from .Scheduler import Scheduler
from .Run import Runs
from .Job import Jobs
from js9 import j

JSBASE = j.application.jsbase_get_class()


def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp


class Repositories(JSBASE):
    def __init__(self, client):
        JSBASE.__init__(self)
        self._client = client
        self._ayscl = client._ayscl

    def list(self):
        """
        List all repositories.

        Returns a list of repository objects.
        """
        ays_repositories = self._ayscl.listRepositories().json()
        repositories = list()
        for repository in ays_repositories:
            repositories.append(Repository(self._client, repository))
        return repositories

    def get(self, name):
        """
        Gets a repository with a give name.

        Args:
            name: name of the repository to retrieve

        Returns a repository object.
        """
        for repository in self.list():
            if repository.model.get('name') == name:
                return repository
        raise ValueError("Could not find repository with name {}".format(name))

    def create(self, name, git):
        """
        Creates a new repository with given name and git repository address.

        Args:
            name: name of the repository to create
            git: url of the Git repository

        Returns a repository object.
        """
        data = {
            'name' : name,
            'git_url' : git
        }

        json_str = json.dumps(data)
        self._ayscl.createRepository(json_str)
        return self.get(name)


class Repository(JSBASE):
    def __init__(self, client, model):
        JSBASE.__init__(self)
        self._client = client
        self._ayscl = client._ayscl
        self.model = model
        self.actorTemplates = ActorTemplates(self)
        self.actors = Actors(self)
        self.blueprints = Blueprints(self)
        self.services = Services(self)
        self.scheduler = Scheduler(self)
        self.runs = Runs(self)
        self.jobs = Jobs(repository=self)

    def destroy(self):
        """
        All services and runs will be deleted, blueprints are kept.
        Make sure to do a commit before you do a distroy, this will give you a chance to roll back.
        """
        try:
            resp = self._ayscl.destroyRepository(data=None, repository=self.model["name"])
        except Exception as e:
            self.logger.error("Error while destroying repository: {}".format(_extract_error(e)))

    def delete(self):
        """
        Delete everything, including the repository itself, all services, runs and blueprints will be lost.
        Make sure to do a commit before you do a delete, this will give you a chance to roll back.
        """
        try:
            resp = self._ayscl.deleteRepository(repository=self.model["name"])
        except Exception as e:
            self.logger.error("Error while deleting repository: {}".format(_extract_error(e)))

    def __repr__(self):
        return "repository: %s" % (self.model["name"])

    __str__ = __repr__
