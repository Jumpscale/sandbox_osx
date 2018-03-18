from io import BytesIO

import etcd3
import yaml
from js9 import j





class EtcdCluster():
    """etced server"""

    def __init__(self, name, dialstrings, mgmtdialstrings, logger=None):

        self.name = name
        self.dialstrings = dialstrings
        self.mgmtdialstrings = mgmtdialstrings
        self._ays = None
        self._client = None

    def _connect(self):
        dialstrings = self.mgmtdialstrings.split(",")
        for dialstring in dialstrings:
            host, port = dialstring.split(":")
            try:
                self._client = etcd3.client(host=host, port=port, timeout=5)
                self._client.status()
                return  # connection is valid
            except (etcd3.exceptions.ConnectionFailedError, etcd3.exceptions.ConnectionTimeoutError) as err:
                self._client = None
                self.logger.error("Could not connect to etcd on %s:%s : %s" % (host, port, str(err)))

        if self._client is None:
            raise RuntimeError("can't connect to etcd on %s" % self.mgmtdialstrings)

    @classmethod
    def from_ays(cls, service, password=None, logger=None):
        logger = logger or default_logger
        logger.debug("create storageEngine from service (%s)", service)

        dialstrings = set()
        for etcd_service in service.producers.get('etcd', []):
            dialstrings.add(etcd_service.model.data.clientBind)

        mgmtdialstrings = set()
        for etcd_service in service.producers.get('etcd', []):
            mgmtdialstrings.add(etcd_service.model.data.mgmtClientBind)

        return cls(
            name=service.name,
            dialstrings=",".join(dialstrings),
            mgmtdialstrings=",".join(mgmtdialstrings),
            logger=logger
        )

    # TODO: replace code duplication with decorator ?

    def put(self, key, value):
        if not self._client:
            self._connect()
        try:
            self._client.put(key, value)
        except (etcd3.exceptions.ConnectionFailedError, etcd3.exceptions.ConnectionTimeoutError):
            self._connect()
            self.put(key, value)

    def delete(self, key):
        if not self._client:
            self._connect()
        try:
            self._client.delete(key)
        except (etcd3.exceptions.ConnectionFailedError, etcd3.exceptions.ConnectionTimeoutError):
            self._connect()
            self.delete(key)

class ETCD():
    """etced server"""

    def __init__(self, name, container, serverBind, clientBind, peers, mgmtClientBind, data_dir='/mnt/data',
                 password=None, logger=None):

        self.name = name
        self.container = container
        self.serverBind = serverBind
        self.clientBind = clientBind
        self.mgmtClientBind = mgmtClientBind
        self.data_dir = data_dir
        self.peers = ",".join(peers)
        self._ays = None
        self._password = None

    @classmethod
    def from_ays(cls, service, password=None, logger=None):
        logger = logger or default_logger
        logger.debug("create storageEngine from service (%s)", service)
        from .Container import Container
        container = Container.from_ays(service.parent, password, logger=service.logger)

        return cls(
            name=service.name,
            container=container,
            serverBind=service.model.data.serverBind,
            clientBind=service.model.data.clientBind,
            mgmtClientBind=service.model.data.mgmtClientBind,
            data_dir=service.model.data.homeDir,
            peers=service.model.data.peers,
            password=password,
            logger=logger
        )

    def start(self):
        configpath = "/etc/etcd_{}.config".format(self.name)

        client_urls = ",".join(list({"http://{}".format(self.clientBind), "http://{}".format(self.mgmtClientBind)}))
        config = {
            "name": self.name,
            "initial-advertise-peer-urls": "http://{}".format(self.serverBind),
            "listen-peer-urls": "http://{}".format(self.serverBind),
            "listen-client-urls": client_urls,
            "advertise-client-urls": client_urls,
            "initial-cluster": self.peers,
            "data-dir": self.data_dir,
            "initial-cluster-state": "new"
        }
        yamlconfig = yaml.safe_dump(config, default_flow_style=False)
        configstream = BytesIO(yamlconfig.encode('utf8'))
        configstream.seek(0)
        self.container.client.filesystem.upload(configpath, configstream)
        cmd = '/bin/etcd --config-file %s' % configpath
        self.container.client.system(cmd, id="etcd.{}".format(self.name))
        if not self.container.is_port_listening(int(self.serverBind.split(":")[1])):
            raise RuntimeError('Failed to start etcd server: {}'.format(self.name))

    def stop(self):
        import time

        if not self.container.is_running():
            return

        jobID = "etcd.{}".format(self.name)
        self.container.client.job.kill(jobID)
        start = time.time()
        while start + 15 > time.time():
            time.sleep(1)
            try:
                self.container.client.job.list(jobID)
            except RuntimeError:
                return
            continue

        raise RuntimeError('failed to stop etcd.')

    def is_running(self):
        jobID = "etcd.{}".format(self.name)
        try:
            self.container.client.job.list(jobID)
        except RuntimeError:
            return False
        return True

    def put(self, key, value):
        if value.startswith("-"):
            value = "-- %s" % value
        if key.startswith("-"):
            key = "-- %s" % key
        cmd = '/bin/etcdctl \
          --endpoints {etcd} \
          put {key} "{value}"'.format(etcd=self.clientBind, key=key, value=value)
        return self.container.client.system(cmd, env={"ETCDCTL_API": "3"}).get()
