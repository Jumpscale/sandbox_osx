import logging
import time
from js9 import j

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class ZeroStor():
    """zerostor server"""

    def __init__(self, name, container, bind='0.0.0.0:8080', data_dir='/mnt/data', meta_dir='/mnt/metadata', max_size_msg=64):

        self.name = name
        self.container = container
        self.bind = bind
        self.data_dir = data_dir
        self.meta_dir = meta_dir
        self.max_size_msg = max_size_msg
        self._ays = None

    @classmethod
    def from_ays(cls, service, password=None):
        logger.debug("create ZeroStor from service (%s)", service)
        from .Container import Container

        container = Container.from_ays(service.parent, password)

        return cls(
            name=service.name,
            container=container,
            bind=service.model.data.bind,
            data_dir=service.model.data.dataDir,
            meta_dir=service.model.data.metaDir,
            max_size_msg=service.model.data.maxSizeMsg,
        )

    def stop(self, timeout=30):
        if not self.container.is_running():
            return

        is_running, job = self.is_running()
        if not is_running:
            return

        logger.debug('stop %s', self)

        self.container.client.job.kill(job['cmd']['id'])

        # wait for StorageEngine to stop
        start = time.time()
        end = start + timeout
        is_running, _ = self.is_running()
        while is_running and time.time() < end:
            time.sleep(1)
            is_running, _ = self.is_running()

        if is_running:
            raise RuntimeError("zerostor server {} didn't stopped")

    def start(self):
        cmd = '/bin/zerostorserver \
            --bind {bind} \
            --data "{datadir}" \
            --meta "{metadir}" \
            --max-msg-size {msgsize} \
            --async-write \
            '.format(bind=self.bind, datadir=self.data_dir, metadir=self.meta_dir, msgsize=self.max_size_msg)
        self.container.client.system(cmd, id="zerostor.{}".format(self.name))
        start = time.time()
        while start + 15 > time.time():
            if self.container.is_port_listening(int(self.bind.split(":")[1])):
                break
            time.sleep(1)
        else:
            raise RuntimeError('Failed to start zerostor server: {}'.format(self.name))

    def is_running(self):
        try:
            if self.port not in self.container.node.freeports(self.port, 1):
                for job in self.container.client.job.list():
                    if 'name' in job['cmd']['arguments'] and job['cmd']['arguments']['name'] == '/bin/zerostorserver':
                        return (True, job)
            return (False, None)
        except Exception as err:
            if str(err).find("invalid container id"):
                return (False, None)
            raise
