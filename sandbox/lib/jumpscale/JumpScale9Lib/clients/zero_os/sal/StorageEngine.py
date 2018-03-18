import io
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class StorageEngine():
    """storageEngine server"""

    def __init__(self, name, container, enabled=True, status='running', bind='0.0.0.0:16379', data_dir='/mnt/data', master=None):
        """
        TODO: write doc string
        """

        self.name = name
        self.bind = bind
        self.enabled = enabled
        self.status = status
        self.master = master
        self.container = container
        self.data_dir = data_dir
        self.master = master
        self._ays = None

    @property
    def port(self):
        return int(self.bind.split(':')[1])

    @classmethod
    def from_ays(cls, service, password=None):
        logger.debug("create storageEngine from service (%s)", service)
        from .Container import Container

        container = Container.from_ays(service.parent, password, logger=service.logger)
        if service.model.data.master != '':
            master_service = service.aysrepo.serviceGet('storage_engine', service.model.data.master)
            master = StorageEngine.from_ays(master_service, password)
        else:
            master = None
        return cls(
            name=service.name,
            container=container,
            enabled=service.model.data.enabled,
            status=service.model.data.status,
            bind=service.model.data.bind,
            data_dir=service.model.data.homeDir,
            master=master,
        )

    def _configure(self):
        logger.debug("configure storageEngine")
        buff = io.BytesIO()
        self.container.client.filesystem.download('/etc/ardb.conf', buff)
        content = buff.getvalue().decode()

        # update config
        content = content.replace('/mnt/data', self.data_dir)
        content = content.replace('0.0.0.0:16379', self.bind)

        mgmt_bind = "%s:%s" % (self.container.node.addr, self.port)
        if self.bind != mgmt_bind:
            content += "server[1].listen %s\n" % mgmt_bind

        if self.master is not None:
            _, port = self.master.bind.split(":")
            content = content.replace('#slaveof 127.0.0.1:6379', 'slaveof {}:{}'.format(self.master.container.node.addr, port))

        # make sure home directory exists
        self.container.client.filesystem.mkdir(self.data_dir)

        # upload new config
        self.container.client.filesystem.upload('/etc/ardb.conf.used', io.BytesIO(initial_bytes=content.encode()))

    def start(self, timeout=100):
        if not self.container.is_running():
            self.container.start()

        running, _ = self.is_running()
        if running:
            return
        logger.debug('start %s', self)

        self._configure()
        self.container.client.system('/bin/ardb-server /etc/ardb.conf.used', id="{}.{}".format("storage_engine", self.name))

        # wait for storageEngine to start
        start = time.time()
        end = start + timeout
        is_running, _ = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running, _ = self.is_running()

        if not is_running:
            raise RuntimeError("storage server {} didn't started".format(self.name))

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
            raise RuntimeError("storage server {} didn't stopped")

    def is_healthy(self):
        import redis
        client = redis.Redis(self.container.node.addr, self.port)
        key = "keytest"
        value = b"some test value"
        if not client.set(key, value):
            return False

        result = client.get(key)
        if result != value:
            return False
        client.delete(key)
        if client.exists(key):
            return False
        return True

    def is_running(self):
        try:
            if self.port not in self.container.node.freeports(self.port, 1):
                for job in self.container.client.job.list():
                    if 'name' in job['cmd']['arguments'] and job['cmd']['arguments']['name'] == '/bin/ardb-server':
                        return (True, job)
            return (False, None)
        except Exception as err:
            if str(err).find("invalid container id"):
                return (False, None)
            raise

    @property
    def ays(self):
        if self._ays is None:
            from JumpScale.sal.g8os.atyourservice.StorageCluster import storageEngineAys
            self._ays = storageEngineAys(self)
        return self._ays

    def __str__(self):
        return "storageEngine <{}>".format(self.name)

    def __repr__(self):
        return str(self)
