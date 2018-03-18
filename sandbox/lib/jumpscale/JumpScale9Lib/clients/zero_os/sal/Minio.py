import redis
import time

from js9 import j

from . import templates


logger = j.logger.get(__name__)


class Minio:
    """
    Minio gateway
    """

    def __init__(self, name, container, zdbs, namespace, private_key, namespace_secret='', addr='0.0.0.0', port=9000):
        """

        :param name: instance name
        :param container: sal of the container running minio
        :param zdbs: a list of zerodbs addresses ex: ['0.0.0.0:9100']
        :param namespace: name of the zerodb namespace
        :param private_key: encryption private key
        :param namespace_secret: secret of the zerodb namespace
        :param addr: ip to bind minio to
        :param port: port to bind minio to
        """
        self.name = name
        self.id = 'minio.{}'.format(self.name)
        self.container = container
        self.addr = addr
        self.port = port
        self.zdbs = zdbs
        self.namespace = namespace
        self.private_key = private_key
        self.namespace_secret = namespace_secret
        self._config_dir = '/bin'
        self._config_name = 'zerostor.yaml'

    def stop(self, timeout=30):
        """
        Stop the minio gateway
        :param timeout: time in seconds to wait for the minio gateway to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.info('stop minio %s' % self.name)

        self.container.client.job.kill(self.id)

        # wait for minio to stop
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if is_running:
            raise RuntimeError('Failed to stop minio server: {}'.format(self.name))

        self.container.node.client.nft.drop_port(self.port)

    def start(self, timeout=15):
        """
        Start minio gatway
        :param timeout: time in seconds to wait for the minio gateway to start
        """
        is_running = self.is_running()
        if is_running:
            return

        logger.info('start minio %s' % self.name)

        cmd = '/bin/minio gateway zerostor --address {addr}:{port} --config-dir {dir}'.format(
            addr=self.addr, port=self.port, dir=self._config_dir)

        # wait for minio to start
        self.container.client.system(cmd, id=self.id)
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if not is_running:
            raise RuntimeError('Failed to start minio server: {}'.format(self.name))

        self.container.node.client.nft.open_port(self.port)

    def is_running(self):
        try:
            for _ in self.container.client.job.list(self.id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    def create_config(self):
        logger.info('Creating minio config for %s' % self.name)
        config = templates.render(
            'minio.conf', namespace=self.namespace, namespace_secret=self.namespace_secret,
            zdbs=self.zdbs, private_key=self.private_key).strip()
        self.container.upload_content(j.sal.fs.joinPaths(self._config_dir, self._config_name), config)
