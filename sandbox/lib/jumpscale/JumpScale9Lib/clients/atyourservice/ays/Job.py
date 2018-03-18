from requests.exceptions import HTTPError
from .Log import Logs
from js9 import j

JSBASE = j.application.jsbase_get_class()


def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp
    
class Jobs(JSBASE):
    def __init__(self, step=None, repository=None):
        JSBASE.__init__(self)
        self._step = step
        if step:
            self._repository = step._run._repository
            self._ayscl = step._run._ayscl
        if repository:
            self._repository = repository
            self._ayscl = repository._ayscl

        # TODO
        # Allow step=None and add filters for showing jobs per actor, repo, service, action, ...

    def list(self):
        """
        List all jobs of a step.

        Returns: list of jobs
        """
        jobs = list()
        if self._step:
            for job in self._step.model['jobs']:
                try:
                    ays_job = self._ayscl.getJob(job['key'], self._repository.model['name'])
                except Exception as e:
                    return _extract_error(e)   
                jobs.append(Job(self._step, job))
            return jobs
                
        if self._repository:
            try:
                resp = self._ayscl.listJobs(self._repository.model['name'])
            except Exception as e:
                return _extract_error(e)
        
            ays_jobs = resp.json()

            for job in ays_jobs:
                try:
                    ays_job = self._ayscl.getJob(job['key'], self._repository.model['name'])
                except Exception as e:
                    return _extract_error(e)
                jobs.append(Job(self._repository, ays_job.json()))
            return jobs

    def get(self, key):
        """
        Get a job by its key.

        Args:
            key: id of the job

        Raises: ValueError if no job with given key could be found

        Returns: job with given key
        """
        for job in self.list():
            if job.model['key'] == key:
                return job
        raise ValueError("Could not find job with key {}".format(key))

class Job(JSBASE):
    def __init__(self, step, model):
        JSBASE.__init__(self)
        self._step = step
        self.model = model
        self.logs = Logs(self)

    def __repr__(self):
        return "job (%s): %s!%s.%s() (%s)" % (self.model["key"], self.model["actor_name"], self.model["service_name"], self.model["action_name"], self.model["state"])

    __str__ = __repr__