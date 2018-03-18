from requests.exceptions import HTTPError
from .Step import Steps
from js9 import j

JSBASE = j.application.jsbase_get_class()


def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp


class Runs(JSBASE):
    def __init__(self, repository):
        JSBASE.__init__(self)
        self._repository = repository
        self._ayscl = repository._ayscl

    def list(self):
        """
        List all runs (keys) sorted by creation date.

        Return: list of runs
        """
        try:
            resp = self._ayscl.listRuns(self._repository.model['name'])
        except Exception as e:
            return _extract_error(e)

        ays_runs = resp.json()
        ays_runs = sorted(ays_runs, key=lambda x: x['epoch'])

        runs = list()
        for run in ays_runs:
            try:
                ays_run = self._ayscl.getRun(run['key'], self._repository.model['name'])
            except Exception as e:
                return _extract_error(e)
            runs.append(Run(self._repository, ays_run.json()))
        return runs

    def create(self, execute=False, callback=None):
        """
        Look for all actions with a state 'scheduled', 'changed' or 'error' and creates a run.
        A run is an collection of actions that will be run on the repository.

        Args:
            execute (True/False): (optional) If true the run will immediately be executed once created; default is False
            callback: (optional) url that will used when finished

        Returns:
            run id, or the HTTP response if nothing to do
        """
        try:
            resp = self._ayscl.createRun(data=None, repository=self._repository.model["name"], query_params={'simulate': True, 'callback_url': callback})
        except Exception as e:
            return _extract_error(e)

        run = resp.json()
        if len(run['steps']) <= 0:
            return resp

        if execute == True:
            try:
                resp = self._ayscl.executeRun(data=None, runid=run['key'], repository=self._repository.model["name"])
            except Exception as e:
                return _extract_error(e)

        return run['key']

    def get(self, key=None):
        """
        Get a run by its key.

        Args:
            key: (optional) id of the run, if no key specified the last run will be returned

        Raises: ValueError if no run with given key could be found

        Returns: run with given key, or last run if no key specified
        """
        for run in self.list():
            if key is None:
                return run
            if run.model['key'] == key:
                return run
        raise ValueError("Could not find run with key {}".format(key))

class Run(JSBASE):
    def __init__(self, repository, model):
        JSBASE.__init__(self)
        self._repository = repository
        self._ayscl = repository._ayscl
        self.model = model
        self.steps = Steps(self)

    def execute(self):
        """
        Execute the run.
        Returns: HTTP response object
        """
        try:
            resp = self._ayscl.executeRun(data=None, runid=self.model['key'], repository=self._repository.model["name"])
        except Exception as e:
             return _extract_error(e)
        return resp

    def delete(self):
        """
        Delete the run.
        Returns: HTTP response object
        """
        try:
            resp = self._ayscl.deleteRun(runid=self.model['key'], repository=self._repository.model["name"])
        except Exception as e:
             return _extract_error(e)
        return resp

    def __repr__(self):
        return "run (%s): %s steps (%s)" % (self.model["key"], len(self.model['steps']), self.model["state"])

    __str__ = __repr__
