import json
import logging
import socket
import uuid

import redis
from js9 import j

from . import typchk
from .AggregatorManager import AggregatorManager
from .BridgeManager import BridgeManager
from .BtrfsManager import BtrfsManager
from .Config import Config
from .ContainerManager import BaseClient, ContainerManager
from .DiskManager import DiskManager
from .KvmManager import KvmManager
from .LogManager import LogManager
from .Nft import Nft
from .Response import Response
from .ZerotierManager import ZerotierManager

DefaultTimeout = 10  # seconds

_config_template = {
    'host': "127.0.0.1",
    'port': 6379,
    'password_': "",
    'db': 0,
    'ssl': True,
    'timeout': 5,
}

JSConfigClientBase = j.tools.configmanager.base_class_config


class Client(BaseClient, JSConfigClientBase):
    _raw_chk = typchk.Checker({
        'id': str,
        'command': str,
        'arguments': typchk.Any(),
        'queue': typchk.Or(str, typchk.IsNone()),
        'max_time': typchk.Or(int, typchk.IsNone()),
        'stream': bool,
        'tags': typchk.Or([str], typchk.IsNone()),
    })

    def __init__(self, instance="main", data={}, parent=None, template=None, ui=None, interactive=True):
        JSConfigClientBase.__init__(self, instance=instance, data=data, parent=parent, template=_config_template, ui=ui, interactive=interactive)
        timeout = self.config.data['timeout']
        BaseClient.__init__(self, timeout=timeout)

        self.__redis = None

        self._container_manager = ContainerManager(self)
        self._bridge_manager = BridgeManager(self)
        self._disk_manager = DiskManager(self)
        self._btrfs_manager = BtrfsManager(self)
        self._zerotier = ZerotierManager(self)
        self._kvm = KvmManager(self)
        self._log_manager = LogManager(self)
        self._nft = Nft(self)
        self._config_manager = Config(self)
        self._aggregator = AggregatorManager(self)

    @property
    def _redis(self):
        if self.__redis is None:
            timeout = self.config.data['timeout']
            socket_timeout = (timeout + 5) if timeout else 15
            socket_keepalive_options = dict()
            if hasattr(socket, 'TCP_KEEPIDLE'):
                socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
            if hasattr(socket, 'TCP_KEEPINTVL'):
                socket_keepalive_options[socket.TCP_KEEPINTVL] = 1
            if hasattr(socket, 'TCP_KEEPIDLE'):
                socket_keepalive_options[socket.TCP_KEEPIDLE] = 1

            self.__redis = redis.Redis(host=self.config.data['host'],
                                       port=self.config.data['port'],
                                       password=self.config.data['password_'],
                                       db=self.config.data['db'], ssl=self.config.data['ssl'],
                                       socket_timeout=socket_timeout,
                                       socket_keepalive=True, socket_keepalive_options=socket_keepalive_options)

        return self.__redis

    @property
    def container(self):
        """
        Container manager
        :return:
        """
        return self._container_manager

    @property
    def bridge(self):
        """
        Bridge manager
        :return:
        """
        return self._bridge_manager

    @property
    def disk(self):
        """
        Disk manager
        :return:
        """
        return self._disk_manager

    @property
    def btrfs(self):
        """
        Btrfs manager
        :return:
        """
        return self._btrfs_manager

    @property
    def zerotier(self):
        """
        Zerotier manager
        :return:
        """
        return self._zerotier

    @property
    def kvm(self):
        """
        KVM manager
        :return:
        """
        return self._kvm

    @property
    def log_manager(self):
        """
        Logger manager
        :return:
        """
        return self._log_manager

    @property
    def nft(self):
        """
        NFT manager
        :return:
        """
        return self._nft

    @property
    def config_manager(self):
        """
        Config manager
        :return:
        """
        return self._config_manager

    @property
    def aggregator(self):
        """
        Aggregator manager
        :return:
        """
        return self._aggregator

    def raw(self, command, arguments, queue=None, max_time=None, stream=False, tags=None, id=None):
        """
        Implements the low level command call, this needs to build the command structure
        and push it on the correct queue.
        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param queue: command queue (commands on the same queue are executed sequentially)
        :param max_time: kill job server side if it exceeded this amount of seconds
        :param stream: If True, process stdout and stderr are pushed to a special queue (stream:<id>) so
            client can stream output
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :return: Response object
        """
        if not id:
            id = str(uuid.uuid4())

        payload = {
            'id': id,
            'command': command,
            'arguments': arguments,
            'queue': queue,
            'max_time': max_time,
            'stream': stream,
            'tags': tags,
        }

        self._raw_chk.check(payload)
        flag = 'result:{}:flag'.format(id)
        self._redis.rpush('core:default', json.dumps(payload))
        if self._redis.brpoplpush(flag, flag, DefaultTimeout) is None:
            TimeoutError('failed to queue job {}'.format(id))
        self.logger.debug('%s >> g8core.%s(%s)', id, command, ', '.join(("%s=%s" % (k, v) for k, v in arguments.items())))

        return Response(self, id)

    def response_for(self, id):
        return Response(self, id)
