import logging
import time
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TfChain:
    """
    TfChain server
    """

    def __init__(self, name, container, data_dir='/mnt/data',
                 rpc_addr='0.0.0.0:23112', api_addr='localhost:23110'):
        self.name = name
        self.id = 'tfchain.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr
        self._daemon = None
        self._client = None

    @property
    def daemon(self):
        if self._daemon is None:
            self._daemon = TfChainDaemon(
                name=self.name,
                container=self.container,
                data_dir=self.data_dir,
                rpc_addr=self.rpc_addr,
                api_addr=self.api_addr,
            )
        return self._daemon

    @property
    def client(self):
        if self._client is None:
            self._client = TfChainClient(
                name=self.name,
                container=self.container,
                addr=self.api_addr,
            )
        return self._client


class TfChainDaemon:
    """
    TfChain Daemon
    """

    def __init__(self, name, container, data_dir='/mnt/data',
                 rpc_addr='0.0.0.0:23112', api_addr='localhost:23110'):
        self.name = name
        self.id = 'tfchaind.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr

    def start(self, timeout=15):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        is_running = self.is_running()
        if is_running:
            return

        cmd = '/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --tfchain-directory {data_dir} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir)

        # wait for tfchain daemon to start
        self.container.client.system(cmd, id=self.id)
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if not self.is_running():
            raise RuntimeError(
                'Failed to start tfchain daemon: {}'.format(self.name))

    def stop(self, timeout=30):
        """
        Stop the tfchain daemon
        :param timeout: time in seconds to wait for the daemon to stop
        """
        if not self.container.is_running():
            return

        is_running = self.is_running()
        if not is_running:
            return

        logger.debug('stop %s', self)
        self.container.stop_job(self.id, signal=signal.SIGINT, timeout=timeout)

    def is_running(self):
        return self.container.is_job_running(self.id)


class TfChainClient:
    """
    TfChain Client
    """

    def __init__(self, name, container, addr='localhost:23110'):
        self.name = name
        self.id = 'tfchainc.{}'.format(self.name)
        self.container = container
        self.addr = addr
        self._recovery_seed = None
        self._wallet_password = None

    @property
    def recovery_seed(self):
        return self._recovery_seed

    @property
    def wallet_password(self):
        return self._wallet_password

    def wallet_init(self):
        output = self.container.client.system(
            '/tfchainc --addr %s wallet init' % self.addr,
            id='%s.wallet_init' % self.id
        ).get()

        output = output.stdout.split('Wallet encrypted with password:\n')
        self._recovery_seed = output[0].split('Recovery seed:\n')[1].strip()
        self._wallet_password = output[1].strip()

    def wallet_unlock(self):
        self.container.client.bash(
            'echo %s | /tfchainc --addr %s wallet unlock' % (self.wallet_password, self.addr),
            id='%s.wallet_unlock' % self.id
        ).get()


class TfChainExplorer:
    """
    TfChain Explorer
    """

    def __init__(self, name, container):
        self.name = name
        self.id = 'tfchainc.{}'.format(self.name)
        self.container = container

    def start(self, timeout=15):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        is_running = self.is_running()
        if is_running:
            return

        cmd = '/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --tfchain-directory {data_dir} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir)

        # wait for tfchain daemon to start
        self.container.client.system(cmd, id=self.id)
        start = time.time()
        end = start + timeout
        is_running = self.is_running()
        while not is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_running()

        if not self.is_running():
            raise RuntimeError(
                'Failed to start tfchain daemon: {}'.format(self.name))