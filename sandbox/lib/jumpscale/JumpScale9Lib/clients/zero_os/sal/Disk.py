from enum import Enum

from .abstracts import Mountable
from .Partition import Partition
from js9 import j

class StorageType(Enum):
    SSD = "SSH"
    HDD = "HDD"
    NVME = "NVME"
    ARCHIVE = "ARCHIVE"
    CDROM = "CDROM"

class Disks():

    """Subobject to list disks"""
    def __init__(self, node):
        self.node = node


    @property
    def client(self):
        return self.node.client

    def list(self):
        """
        List of disks on the node
        """
        disks = []
        disk_list = self.client.disk.list()
        if 'blockdevices' in disk_list:
            for disk_info in self.client.disk.list()['blockdevices']:
                disks.append(Disk(
                    node=self.node,
                    disk_info=disk_info
                ))
        return disks

    def get(self, name):
        """
        return the disk called `name`
        @param name: name of the disk
        """
        for disk in self.list():
            if disk.name == name:
                return disk
        return None


class Disk(Mountable):
    """Disk in a Zero-OS"""

    def __init__(self, node, disk_info):
        """
        disk_info: dict returned by client.disk.list()
        """
        # g8os client to talk to the node
        Mountable.__init__(self)
        self.node = node
        self.name = None
        self.size = None
        self.blocksize = None
        self.partition_table = None
        self.mountpoint = None
        self.model = None
        self._filesystems = []
        self.type = None
        self.partitions = []
        self.transport = None

        self._load(disk_info)

    @property
    def client(self):
        return self.node.client

    @property
    def devicename(self):
        return "/dev/{}".format(self.name)

    @property
    def filesystems(self):
        self._populate_filesystems()
        return self._filesystems

    def _load(self, disk_info):
        self.name = disk_info['name']
        detail = self.client.disk.getinfo(self.name)
        self.size = int(disk_info['size'])
        self.blocksize = detail['blocksize']
        if detail['table'] != 'unknown':
            self.partition_table = detail['table']
        self.mountpoint = disk_info['mountpoint']
        self.model = disk_info['model']
        self.type = self._disk_type(disk_info)
        self.transport = disk_info['tran']
        for partition_info in disk_info.get('children', []) or []:
            self.partitions.append(
                Partition(
                    disk=self,
                    part_info=partition_info)
            )

    def _populate_filesystems(self):
        """
        look into all the btrfs filesystem and populate
        the filesystems attribute of the class with the detail of
        all the filesystem present on the disk
        """
        self._filesystems = []
        for fs in (self.client.btrfs.list() or []):
            for device in fs['devices']:
                if device['path'] == "/dev/{}".format(self.name):
                    self._filesystems.append(fs)
                    break

    def _disk_type(self, disk_info):
        """
        return the type of the disk
        """
        if disk_info['rota'] == "1":
            if disk_info['type'] == 'rom':
                return StorageType.CDROM
            # assume that if a disk is more than 7TB it's a SMR disk
            elif int(disk_info['size']) > (1024 * 1024 * 1024 * 1024 * 7):
                return StorageType.ARCHIVE
            else:
                return StorageType.HDD
        else:
            if "nvme" in disk_info['name']:
                return StorageType.NVME
            else:
                return StorageType.SSD

    def mktable(self, table_type='gpt', overwrite=False):
        """
        create a partition table on the disk
        @param table_type: Partition table type as accepted by parted
        @param overwrite: erase any existing partition table
        """
        if self.partition_table is not None and overwrite is False:
            return

        self.client.disk.mktable(
            disk=self.name,
            table_type=table_type
        )

    def mkpart(self, start, end, part_type="primary"):
        """
        @param start: partition start as accepted by parted mkpart
        @param end: partition end as accepted by parted mkpart
        @param part_type: partition type as accepted by parted mkpart
        """
        before = {p.name for p in self.partitions}

        self.client.disk.mkpart(
            self.name,
            start=start,
            end=end,
            part_type=part_type,
        )
        after = {}
        for disk in self.client.disk.list()['blockdevices']:
            if disk['name'] != self.name:
                continue
            for part in disk.get('children', []):
                after[part['name']] = part
        name = set(after.keys()) - before

        part_info = after[list(name)[0]]
        partition = Partition(
            disk=self,
            part_info=part_info)
        self.partitions.append(partition)

        return partition

    def __str__(self):
        return "Disk <{}>".format(self.name)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.devicename == other.devicename
