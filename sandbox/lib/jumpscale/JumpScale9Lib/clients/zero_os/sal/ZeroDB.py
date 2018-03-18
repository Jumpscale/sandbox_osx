import redis
import time

from js9 import j

logger = j.logger.get(__name__)


class ZeroDB:
    """
    ZeroDB server
    """

    def __init__(self, name, container, port=9900, data_dir='/mnt/data',
                 index_dir='/mnt/index', mode='user', sync=False, admin=''):
        self.name = name
        self.id = 'zerodb.{}'.format(self.name)
        self.container = container
        self.port = port
        self.data_dir = data_dir
        self.index_dir = index_dir
        self.mode = mode
        self.sync = sync
        self.admin = admin
        self.__redis = None

    @property
    def _redis(self):
        if self.__redis is None:
            self.__redis = redis.Redis(host=self.container.node.addr, port=self.port, password=self.admin)
        return self.__redis

    def stop(self, timeout=30):
        """
        Stop the zerodb server
        :param timeout: time in seconds to wait for the zerodb server to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.info('stop zerodb %s' % self.name)

        self.container.client.job.kill(self.id)

        # wait for zerodb to stop
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if is_running:
            raise RuntimeError('Failed to stop zerodb server: {}'.format(self.name))

        self.container.node.client.nft.drop_port(self.port)

    def start(self, timeout=15):
        """
        Start zero db server
        :param timeout: time in seconds to wait for the zerodb server to start
        """
        is_running = self.is_running()
        if is_running:
            return

        logger.info('start zerodb %s' % self.name)

        cmd = '/bin/zdb \
            --port {port} \
            --data {data_dir} \
            --index {index_dir} \
            --mode {mode} \
            '.format(port=self.port, data_dir=self.data_dir, index_dir=self.index_dir, mode=self.mode)
        if self.sync:
            cmd += ' --sync'
        if self.admin:
            cmd += ' --admin {}'.format(self.admin)

        # wait for zerodb to start
        self.container.client.system(cmd, id=self.id)
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if not is_running:
            raise RuntimeError('Failed to start zerodb server: {}'.format(self.name))

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

    def list_namespaces(self):
        logger.info('listing namespaces for zerodb %s' % self.name)

        namespaces = self._redis.execute_command('NSLIST')
        return [namespace.decode('utf-8') for namespace in namespaces]

    def get_namespace_info(self, namespace):
        logger.info('get namespace %s info for zerodb %s' % (namespace, self.name))

        info = self._redis.execute_command('NSINFO', namespace).decode('utf-8')
        info = info.replace('# namespace\n', '')
        info_lines = info.splitlines()
        result = {}
        for info_line in info_lines:
            info_split = info_line.split(':')
            result[info_split[0].strip()] = info_split[1].strip()

        return result

    def create_namespace(self, namespace):
        logger.info('create namespace %s for zerodb %s' % (namespace, self.name))
        self._redis.execute_command('NSNEW', namespace)

    def set_namespace_property(self, namespace, prop, value):
        logger.info('set namespace %s property for zerodb %s' % (namespace, self.name))

        if prop not in ['maxsize', 'password', 'public']:
            raise ValueError('Namespace property must be maxsize, password or public')
        self._redis.execute_command('NSSET', namespace, prop, value)
