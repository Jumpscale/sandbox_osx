import time
from collections import namedtuple
from datetime import datetime
from io import BytesIO

import netaddr
import redis
from js9 import j
from JumpScale9Lib.clients.zero_os.Client import Client

from .Capacity import Capacity
from .Container import Containers
from .Disk import Disks, StorageType
from .healthcheck import HealthCheck
from .Network import Network
from .StoragePool import StoragePools

Mount = namedtuple('Mount', ['device', 'mountpoint', 'fstype', 'options'])
logger = j.logger.get(__name__)


class Node():
    """Represent a Zero-OS Server"""

    def __init__(self, client):
        # g8os client to talk to the node
        self._storageAddr = None
        self.addr = client.config.data['host']
        self.port = client.config.data['port']
        self.disks = Disks(self)
        self.storagepools = StoragePools(self)
        self.containers = Containers(self)
        self.network = Network(self)
        self.healthcheck = HealthCheck(self)
        self.capacity = Capacity(self)
        self.client = client


    @property
    def name(self):
        def get_nic_hwaddr(nics, name):
            for nic in nics:
                if nic['name'] == name:
                    return nic['hardwareaddr']

        defaultgwdev = self.client.bash("ip route | grep default | awk '{print $5}'", max_time=60).get().stdout.strip()
        nics = self.client.info.nic()
        macgwdev = None
        if defaultgwdev:
            macgwdev = get_nic_hwaddr(nics, defaultgwdev)
        if not macgwdev:
            raise AttributeError("name not find for node {}".format(self))
        return macgwdev.replace(":", '')

    @property
    def storageAddr(self):
        if not self._storageAddr:
            nic_data = self.client.info.nic()
            for nic in nic_data:
                if nic['name'] == 'backplane':
                    for ip in nic['addrs']:
                        network = netaddr.IPNetwork(ip['addr'])
                        if network.version == 4:
                            self._storageAddr = network.ip.format()
                            return self._storageAddr
            self._storageAddr = self.addr
        return self._storageAddr

    def get_nic_by_ip(self, addr):
        try:
            res = next(nic for nic in self.client.info.nic() if any(addr == a['addr'].split('/')[0] for a in nic['addrs']))
            return res
        except StopIteration:
            return None

    def _eligible_fscache_disk(self, disks):
        """
        return the first disk that is eligible to be used as filesystem cache
        First try to find a ssd disk, otherwise return a HDD
        """
        priorities = [StorageType.SSD, StorageType.HDD, StorageType.NVME]
        eligible = {t: [] for t in priorities}
        # Pick up the first ssd
        usedisks = []
        for pool in (self.client.btrfs.list() or []):
            for device in pool['devices']:
                usedisks.append(device['path'])
        for disk in disks[::-1]:
            if disk.devicename in usedisks or len(disk.partitions) > 0:
                continue
            if disk.type in priorities:
                eligible[disk.type].append(disk)
        # pick up the first disk according to priorities
        for t in priorities:
            if eligible[t]:
                return eligible[t][0]
        else:
            raise RuntimeError("cannot find eligible disks for the fs cache")

    def find_disks(self, disk_type):
        """
        return a list of disk that are not used by storage pool
        or has a different type as the one required for this cluster
        """
        available_disks = {}
        for disk in self.disks.list():
            # skip disks of wrong type
            if disk.type.name != disk_type:
                continue
            # skip devices which have filesystems on the device
            if len(disk.filesystems) > 0:
                continue

            # include devices which have partitions
            if len(disk.partitions) == 0:
                available_disks.setdefault(self.name, []).append(disk)

        return available_disks

    def _mount_fscache(self, storagepool):
        """
        mount the fscache storage pool and copy the content of the in memmory fs inside
        """
        mountedpaths = [mount.mountpoint for mount in self.list_mounts()]

        def create_cache_dir(path, name):
            self.client.filesystem.mkdir(path)
            if path not in mountedpaths:
                if storagepool.exists(name):
                    storagepool.get(name).delete()
                fs = storagepool.create(name)
                self.client.disk.mount(storagepool.devicename, path, ['subvol={}'.format(fs.subvolume)])

        create_cache_dir('/var/cache/containers', 'containercache')
        create_cache_dir('/var/cache/vm', 'vmcache')

        logpath = '/var/log'
        if logpath not in mountedpaths:
            # logs is empty filesystem which we create a snapshot on to store logs of current boot
            snapname = '{:%Y-%m-%d-%H-%M}'.format(datetime.now())
            fs = storagepool.get('logs')
            snapshot = fs.create(snapname)
            self.client.bash('mkdir /tmp/log && mv /var/log/* /tmp/log/')
            self.client.disk.mount(storagepool.devicename, logpath, ['subvol={}'.format(snapshot.subvolume)])
            self.client.bash('mv /tmp/log/* /var/log/').get()
            self.client.log_manager.reopen()
            # startup syslogd and klogd
            self.client.system('syslogd -n -O /var/log/messages')
            self.client.system('klogd -n')

    def freeports(self, baseport=2000, nrports=3):
        ports = self.client.info.port()
        usedports = set()
        for portInfo in ports:
            if portInfo['network'] != "tcp":
                continue
            usedports.add(portInfo['port'])

        freeports = []
        while True:
            if baseport not in usedports:
                freeports.append(baseport)
                if len(freeports) >= nrports:
                    return freeports
            baseport += 1

    def find_persistance(self, name='fscache'):
        fscache_sp = None
        for sp in self.storagepools.list():
            if sp.name == name:
                fscache_sp = sp
                break
        return fscache_sp

    def is_configured(self, name=None):
        if not name:
            name = self.name
        poolname = '{}_fscache'.format(name)
        fscache_sp = self.find_persistance(poolname)
        if fscache_sp is None:
            return False
        return bool(fscache_sp.mountpoint)

    def partition_and_mount_disks(self, name='fscache'):
        fscache_sp = self.find_persistance(name)
        cache_devices = fscache_sp.devices if fscache_sp else []
        mounts = []
        node_mountpoints = self.client.disk.mounts()

        for disk in self.disks.list():
            # this check is there to be able to test with a qemu setup
            if disk.model == 'QEMU HARDDISK   ':
                continue

            # temporary fix to ommit overwriting the usb boot disk
            if disk.transport == 'usb':
                continue

            if not disk.partitions:
                sp = self.storagepools.create(disk.name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
                devicename = sp.devices[0]
            else:
                if len(disk.partitions) > 1:
                    raise RuntimeError('Found more than 1 partition for disk %s' % disk.name)

                partition = disk.partitions[0]
                devicename = partition.devicename
                sps = self.storagepools.list(devicename)
                if len(sps) > 1:
                    raise RuntimeError('Found more than 1 storagepool for device %s' % devicename)
                elif not sps:
                    sp = self.storagepools.create(disk.name, devices=[devicename], metadata_profile='single', data_profile='single', overwrite=True)
                else:
                    sp = sps[0]

            sp.mount()
            if sp.exists(disk.name):
                fs = sp.get(disk.name)
            else:
                fs = sp.create(disk.name)

            mount_point = '/mnt/zdbs/{}'.format(disk.name)
            self.client.filesystem.mkdir(mount_point)

            device_mountpoints = node_mountpoints.get(devicename, [])
            for device_mountpoint in device_mountpoints:
                if device_mountpoint['mountpoint'] == mount_point:
                    break
            else:
                subvol = 'subvol={}'.format(fs.subvolume)
                self.client.disk.mount(sp.devicename, mount_point, [subvol])

            mounts.append({'disk': disk.name, 'mountpoint': mount_point})

        return mounts

    def ensure_persistance(self, name='fscache'):
        """
        look for a disk not used,
        create a partition and mount it to be used as cache for the g8ufs
        set the label `fs_cache` to the partition
        """
        disks = self.disks.list()
        if len(disks) <= 0:
            # if no disks, we can't do anything
            return

        # check if there is already a storage pool with the fs_cache label
        fscache_sp = self.find_persistance(name)

        # create the storage pool if we don't have one yet
        if fscache_sp is None:
            disk = self._eligible_fscache_disk(disks)
            fscache_sp = self.storagepools.create(name, devices=[disk.devicename], metadata_profile='single', data_profile='single', overwrite=True)
        fscache_sp.mount()
        try:
            fscache_sp.get('logs')
        except ValueError:
            fscache_sp.create('logs')

        # mount the storage pool
        self._mount_fscache(fscache_sp)
        return fscache_sp

    def download_content(self, remote):
        buff = BytesIO()
        self.client.filesystem.download(remote, buff)
        return buff.getvalue().decode()

    def upload_content(self, remote, content):
        if isinstance(content, str):
            content = content.encode('utf8')
        bytes = BytesIO(content)
        self.client.filesystem.upload(remote, bytes)

    def wipedisks(self):
        logger.debug('Wiping node {hostname}'.format(**self.client.info.os()))
        mounteddevices = {mount['device']: mount for mount in self.client.info.disk()}

        def getmountpoint(device):
            for mounteddevice, mount in mounteddevices.items():
                if mounteddevice.startswith(device):
                    return mount

        jobs = []
        for disk in self.client.disk.list()['blockdevices']:
            devicename = '/dev/{}'.format(disk['kname'])
            if disk['tran'] == 'usb':
                logger.debug('   * Not wiping usb {kname} {model}'.format(**disk))
                continue
            mount = getmountpoint(devicename)
            if not mount:
                logger.debug('   * Wiping disk {kname}'.format(**disk))
                jobs.append(self.client.system('dd if=/dev/zero of={} bs=1M count=50'.format(devicename)))
            else:
                logger.debug('   * Not wiping {device} mounted at {mountpoint}'.format(device=devicename, mountpoint=mount['mountpoint']))

        # wait for wiping to complete
        for job in jobs:
            job.get()

    def list_mounts(self):
        allmounts = []
        for mount in self.client.info.disk():
            allmounts.append(Mount(mount['device'],
                                   mount['mountpoint'],
                                   mount['fstype'],
                                   mount['opts']))
        return allmounts

    def is_running(self):
        state = False
        start = time.time()
        err = None
        while time.time() < start + 30:
            try:
                self.client.testConnectionAttempts = 0
                state = self.client.ping()
                break
            except (RuntimeError, ConnectionError, redis.ConnectionError, redis.TimeoutError, TimeoutError) as error:
                err = error
                time.sleep(1)
        else:
            logger.debug("Could not ping %s within 30 seconds due to %s" % (self.addr, err))

        return state

    def __str__(self):
        return "Node <{host}:{port}>".format(
            host=self.addr,
            port=self.port,
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        a = "{}:{}".format(self.addr, self.port)
        b = "{}:{}".format(other.addr, other.port)
        return a == b

    def __hash__(self):
        return hash((self.addr, self.port))
