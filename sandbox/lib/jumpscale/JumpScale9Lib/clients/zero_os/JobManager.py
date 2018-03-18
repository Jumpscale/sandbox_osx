import signal

from . import typchk
from js9 import j




class JobManager():
    _job_chk = typchk.Checker({
        'id': typchk.Or(str, typchk.IsNone()),
    })

    _kill_chk = typchk.Checker({
        'id': str,
        'signal': int,
    })
    def __init__(self, client):
        self._client = client


    def list(self, id=None):
        """
        List all running jobs

        :param id: optional ID for the job to list
        """
        args = {'id': id}
        self._job_chk.check(args)
        return self._client.json('job.list', args)

    def kill(self, id, signal=signal.SIGTERM):
        """
        Kill a job with given id

        :WARNING: beware of what u kill, if u killed redis for example core0 or coreX won't be reachable

        :param id: job id to kill
        """
        args = {
            'id': id,
            'signal': int(signal),
        }
        self._kill_chk.check(args)
        return self._client.json('job.kill', args)
