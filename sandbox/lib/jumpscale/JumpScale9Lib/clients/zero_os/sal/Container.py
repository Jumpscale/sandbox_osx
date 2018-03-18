import logging
import time
from io import BytesIO
from js9 import j
import signal

logging.basicConfig(level=logging.INFO)
default_logger = logging.getLogger(__name__)


class Containers():
    def __init__(self, node, logger=None):
        self.node = node

    def list(self):
        containers = []
        for container in self.node.client.container.list().values():
            try:
                containers.append(Container.from_containerinfo(container, self.node))
            except ValueError:
                # skip containers withouth tags
                pass
        return containers

    def get(self, name):
        containers = list(self.node.client.container.find(name).values())
        if not containers:
            raise LookupError("Could not find container with name {}".format(name))
        if len(containers) > 1:
            raise LookupError("Found more than one containter with name {}".format(name))
        return Container.from_containerinfo(containers[0], self.node)

    def create(self, name, flist, hostname=None, mounts=None, nics=None,
               host_network=False, ports=None, storage=None, init_processes=None, privileged=False, env=None):
        container = Container(name, self.node, flist, hostname, mounts, nics,
                              host_network, ports, storage, init_processes, privileged, env=env)
        container.start()
        return container


class Container():
    """G8SO Container"""

    def __init__(self, name, node, flist, hostname=None, mounts=None, nics=None,
                 host_network=False, ports=None, storage=None, init_processes=None,
                 privileged=False, identity=None, env=None, logger=None):
        """
        TODO: write doc string
        filesystems: dict {filesystemObj: target}
        """

        self.name = name
        self.node = node
        self.mounts = mounts or {}
        self.hostname = hostname
        self.flist = flist
        self.ports = ports or {}
        self.nics = nics or []
        self.host_network = host_network
        self.storage = storage
        self.init_processes = init_processes or []
        self.privileged = privileged
        self.identity = identity
        self.env = env or {}
        self._client = None
        self.logger = logger or default_logger

        self._ays = None
        for nic in self.nics:
            nic.pop('token', None)
            if nic.get('config', {}).get('gateway', ''):
                nic['monitor'] = True

    @classmethod
    def from_containerinfo(cls, containerinfo, node, logger=None):
        logger = logger or default_logger
        logger.debug("create container from info")

        arguments = containerinfo['container']['arguments']
        if not arguments['tags']:
            # we don't deal with tagless containers
            raise ValueError("Could not load containerinfo withouth tags")
        return cls(arguments['name'],
                   node,
                   arguments['root'],
                   arguments['hostname'],
                   arguments['mount'],
                   arguments['nics'],
                   arguments['host_network'],
                   arguments['port'],
                   arguments['storage'],
                   arguments['privileged'],
                   arguments['identity'],
                   arguments['env'],
                   logger=logger)

    @classmethod
    def from_ays(cls, service, password=None, logger=None, timeout=120):
        logger = logger or default_logger
        logger.debug("create container from service (%s)", service)
        from .Node import Node
        node = Node.from_ays(service.parent, password, timeout)
        ports = {}
        for portmap in service.model.data.ports:
            source, dest = portmap.split(':')
            ports[int(source)] = int(dest)
        nics = [nic.to_dict() for nic in service.model.data.nics]
        mounts = service.model.data.to_dict().get('mounts', [])
        for mount in mounts:
            fs_service = service.aysrepo.serviceGet('filesystem', mount['filesystem'])
            mount['storagepool'] = fs_service.parent.name

        container = cls(
            name=service.name,
            node=node,
            mounts=mounts,
            nics=nics,
            hostname=service.model.data.hostname,
            flist=service.model.data.flist,
            ports=ports,
            host_network=service.model.data.hostNetworking,
            storage=service.model.data.storage,
            init_processes=[p.to_dict() for p in service.model.data.initProcesses],
            privileged=service.model.data.privileged,
            identity=service.model.data.identity,
            logger=logger
        )
        return container

    @property
    def id(self):
        self.logger.debug("get container id")
        info = self.info
        if info:
            return info['container']['id']
        return

    @property
    def info(self):
        self.logger.debug("get container info")
        for containerid, container in self.node.client.container.list().items():
            if self.name in (container['container']['arguments']['tags'] or []):
                container['container']['id'] = int(containerid)
                return container
        return

    @property
    def client(self):
        if not self._client:
            self._client = self.node.client.container.client(self.id)
        return self._client

    def upload_content(self, remote, content):
        if isinstance(content, str):
            content = content.encode('utf8')
        bytes = BytesIO(content)
        self.client.filesystem.upload(remote, bytes)

    def download_content(self, remote):
        buff = BytesIO()
        self.client.filesystem.download(remote, buff)
        return buff.getvalue().decode()

    def _create_container(self, timeout=60):
        self.logger.debug("send create container command to zero-os (%s)", self.flist)
        tags = [self.name]
        if self.hostname and self.hostname != self.name:
            tags.append(self.hostname)

        # Populate the correct mounts dict if this instance was created using the `from_ays` function.
        if type(self.mounts) == list:
            mounts = {}
            for mount in self.mounts:
                try:
                    sp = self.node.storagepools.get(mount['storagepool'])
                    fs = sp.get(mount['filesystem'])
                except KeyError:
                    continue
                mounts[fs.path] = mount['target']
            self.mounts = mounts

        job = self.node.client.container.create(
            root_url=self.flist,
            mount=self.mounts,
            host_network=self.host_network,
            nics=self.nics,
            port=self.ports,
            tags=tags,
            name=self.name,
            hostname=self.hostname,
            storage=self.storage,
            privileged=self.privileged,
            identity=self.identity,
            env=self.env
        )

        containerid = job.get(timeout)

    def is_job_running(self, id):
        try:
            for _ in self.client.job.list(id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    def stop_job(self, id, signal=signal.SIGTERM, timeout=30):
        is_running = self.is_job_running(id)
        if not is_running:
            return

        self.logger.debug('stop job: %s', id)

        self.client.job.kill(self.id)

        # wait for the daemon to stop
        start = time.time()
        end = start + timeout
        is_running = self.is_job_running(id)
        while is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_job_running(id)

        if is_running:
            raise RuntimeError('Failed to stop job {}'.format(id))

    def is_port_listening(self, port, timeout=60):
        import time
        start = time.time()
        while start + timeout > time.time():
            if port not in self.node.freeports(port, nrports=3):
                return True
            time.sleep(0.2)
        return False

    def start(self):
        if not self.is_running():
            self.logger.debug("start %s", self)
            self._create_container()
            for process in self.init_processes:
                cmd = "{} {}".format(process['name'], ' '.join(process.get('args', [])))
                pwd = process.get('pwd', '')
                stdin = process.get('stdin', '')
                id = process.get('id')
                env = {}
                for x in process.get('environment', []):
                    k, v = x.split("=")
                    env[k] = v
                self.client.system(command=cmd, dir=pwd, stdin=stdin, env=env, id=id)

    def stop(self):
        if not self.is_running():
            return
        self.logger.debug("stop %s", self)

        self.node.client.container.terminate(self.id)

    def is_running(self):
        return self.node.is_running() and self.id is not None

    @property
    def ays(self):
        if self._ays is None:
            from JumpScale.sal.g8os.atyourservice.StorageCluster import ContainerAYS
            self._ays = ContainerAYS(self)
        return self._ays

    def waitOnJob(self, job):
        MAX_LOG = 15
        logs = []

        def callback(lvl, message, flag):
            if len(logs) == MAX_LOG:
                logs.pop(0)
            logs.append(message)

            if flag & 0x4 != 0:
                erroMessage = " ".join(logs)
                raise RuntimeError(erroMessage)
        resp = self.client.subscribe(job.id)
        resp.stream(callback)

    def __str__(self):
        return "Container <{}>".format(self.name)

    def __repr__(self):
        return str(self)
