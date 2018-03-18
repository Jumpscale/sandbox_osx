from requests.exceptions import HTTPError
from .Run import Run
from js9 import j

JSBASE = j.application.jsbase_get_class()


def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp


class Scheduler(JSBASE):
    def __init__(self, repository):
        JSBASE.__init__(self)
        self._repository = repository
        self._ayscl = repository._ayscl
    
    def getStatus(self):
        """
        Returns status of repository from the scheduler
        """
        try:
            resp = self._ayscl.getSchedulerStatus(self._repository.model['name'])
        except Exception as e:
                return _extract_error(e)
        info = resp.json()
        status = info['status']
        return status

    def getQueueSize(self):
        """
        Returns queue size of repository from the scheduler
        """
        try:
            resp = self._ayscl.getSchedulerStatus(self._repository.model['name'])
        except Exception as e:
                return _extract_error(e)
        info = resp.json()
        qsize = info['queueSize']
        return qsize
        

    def getCurrentRun(self):
        """
        Returns current run from the scheduler
        """
        try:
            resp = self._ayscl.getCurrentRun(self._repository.model['name'])
        except Exception as e:
                return _extract_error(e)
        if resp.status_code == 204:
            return None
        return Run(self._repository, resp.json())