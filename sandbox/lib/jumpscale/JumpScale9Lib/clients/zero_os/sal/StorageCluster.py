import json
import logging
import os

from js9 import j

from .Node import Node
from .StorageEngine import StorageEngine
from .StoragePool import StoragePool
from .ZeroStor import ZeroStor

logging.basicConfig(level=logging.INFO)
default_logger = logging.getLogger(__name__)



class BaseStorageCluster():
    def __init__(self, label, nodes, nr_servers, storage_servers=None, logger=None):
        self.label = label
        self.name = label
        self.nodes = nodes or []
        self.nr_servers = nr_servers
        self.storage_servers = storage_servers or []


    @classmethod
    def from_ays(cls, service, password, logger=None):
        pass

    @property
    def dashboard(self):
        board = StorageDashboard(self)
        return board.template


    def start(self):
        self.logger.debug("start %s", self)
        for server in self.storage_servers:
            server.start()

    def stop(self):
        self.logger.debug("stop %s", self)
        for server in self.storage_servers:
            server.stop()

    def is_running(self):
        for server in self.storage_servers:
            if not server.is_running():
                return False
        return True

    def __str__(self):
        return "StorageCluster <{}>".format(self.label)

    def __repr__(self):
        return str(self)

    def get_disks(self, available_disks):
        pass


class ObjectCluster(BaseStorageCluster):
    def __init__(self, label, nodes, nr_servers, data_disk_type, meta_disk_type, servers_per_meta_drive, storage_servers, storage_pools=[], logger=None):
        super().__init__(label, nodes, nr_servers, storage_servers)
        self.data_disk_type = data_disk_type
        self.meta_disk_type = meta_disk_type
        self.servers_per_meta_drive = servers_per_meta_drive
        self.storage_pools = storage_pools

    @classmethod
    def from_ays(cls, service, password, logger=None):
        logger = logger or default_logger
        logger.debug("load cluster storage cluster from service (%s)", service)
        data_disk_type = str(service.model.data.dataDiskType)
        meta_disk_type = str(service.model.data.metaDiskType)
        servers_per_meta_drive = service.model.data.serversPerMetaDrive

        storage_servers = set()
        for storageEngine_service in service.producers.get('zerostor', []):
            storages_server = ZeroStor.from_ays(storageEngine_service, password)
            storage_servers.add(storages_server)

        storage_pools = set()
        for storagePool_service in service.producers.get('storagepool', []):
            storage_pool = StoragePool.from_ays(storagePool_service, password)
            storage_pools.add(storage_pool)

        nodes = set()
        for node_service in service.producers["node"]:
            nodes.add(Node.from_ays(node_service, password))

        cluster = cls(label=service.name,
                      nodes=list(nodes),
                      storage_servers=list(storage_servers),
                      nr_servers=service.model.data.nrServer,
                      data_disk_type=data_disk_type,
                      meta_disk_type=meta_disk_type,
                      servers_per_meta_drive=servers_per_meta_drive,
                      storage_pools=storage_pools,
                      logger=logger)

        return cluster

    def get_disks(self, data_available_disks, meta_available_disks):
        """
        Get disks to be used by StorageEngine, 0-stor
        It takes into account that 0-stor data, 0-stor meta disks can be of different types
        """
        import math

        # diskmap example: {hdd: {node: [vda, vdb, vdc]}}
        diskmap = {}
        diskmap[self.data_disk_type] = data_available_disks
        diskmap[self.meta_disk_type] = meta_available_disks

        data_disks_per_node = self.nr_servers // len(self.nodes)
        meta_disks_per_node = math.ceil(data_disks_per_node / self.servers_per_meta_drive)

        datadisks = self._get_disks_from_map(diskmap[self.data_disk_type], data_disks_per_node, self.data_disk_type)
        metadisks = self._get_disks_from_map(diskmap[self.meta_disk_type], meta_disks_per_node, self.meta_disk_type)

        return datadisks, metadisks

    def _get_disks_from_map(self, diskmap, diskspernode, disktype):
        _disks = {}
        for node, disks in diskmap.items():
            if len(disks) < diskspernode:
                raise ValueError("Not enough available {} disks on node {}".format(disktype, node))
            _disks[node] = disks[:diskspernode]
            diskmap[node] = diskmap[node][diskspernode:]
        return _disks


class BlockCluster(BaseStorageCluster):
    """BlockCluster is a cluster of StorageEngine servers"""

    def __init__(self, label, nr_servers, disk_type, nodes=None, storage_pools=[], storage_servers=None, logger=None):
        """
        @param label: string repsenting the name of the storage cluster
        """
        BaseStorageCluster.__init__(self, label, nodes, nr_servers, storage_servers)
        self.label = label
        self.name = label
        self.nodes = nodes or []
        self.filesystems = []
        self.nr_servers = nr_servers
        self.storage_servers = storage_servers or []
        self.disk_type = disk_type
        self._ays = None
        self.storage_pools = storage_pools if storage_pools else []


    @classmethod
    def from_ays(cls, service, password, logger=None):
        logger = logger or default_logger
        logger.debug("load cluster storage cluster from service (%s)", service)

        storage_servers = set()
        for storageEngine_service in service.producers.get('storage_engine', []):
            storages_server = StorageEngine.from_ays(storageEngine_service, password)
            storage_servers.add(storages_server)

        storage_pools = set()
        for storagePool_service in service.producers.get('storagepool', []):
            storage_pool = StoragePool.from_ays(storagePool_service, password)
            storage_pools.add(storage_pool)

        nodes = set()
        for node_service in service.producers["node"]:
            nodes.add(Node.from_ays(node_service, password))

        cluster = cls(label=service.name,
                      nodes=list(nodes),
                      storage_servers=list(storage_servers),
                      logger=logger,
                      disk_type=service.model.data.diskType,
                      nr_servers=service.model.data.nrServer,
                      storage_pools=storage_pools)
        cluster.storage_servers = storage_servers
        return cluster

    def get_config(self):
        data = {'dataStorage': [],
                'label': self.name,
                'status': 'ready' if self.is_running() else 'error',
                'nodes': [node.name for node in self.nodes]}
        for storageserver in self.storage_servers:
            data['dataStorage'].append({'address': storageserver.bind})
        return data

    def get_disks(self, available_disks):
        """
        Get disks to be used by StorageEngine
        """
        # available_disks example: {node: [vda, vdb, vdc]}

        disks_per_node = self.nr_servers // len(self.nodes)

        diskmap = {}
        for node, disks in available_disks.items():
            if self.nr_servers > len(disks):
                raise ValueError("Not enough available {} disks on node {}".format(self.disk_type, node))
            diskmap[node] = disks[:disks_per_node]

        return diskmap

    def health(self):
        """
        Return a view of the state all storage server running in this cluster
        example :
        {
        'cluster1_1': {'storageEngine': True, 'container': True},
        'cluster1_2': {'storageEngine': True, 'container': True},
        }
        """
        health = {}
        for server in self.storage_servers:
            running, _ = server.is_running()
            health[server.name] = {
                'storageEngine': running,
                'container': server.container.is_running(),
            }
        return health


class StorageServer():
    """StorageEngine servers"""

    def __init__(self, cluster, logger=None):
        self.cluster = cluster
        self.container = None
        self.storageEngine = None


    @classmethod
    def from_ays(cls, storageEngine_services, password=None, logger=None):
        storageEngine = StorageEngine.from_ays(storageEngine_services, password)
        storage_server = cls(None, logger)
        storage_server.container = storageEngine.container
        storage_server.storageEngine = storageEngine
        return storage_server

    @property
    def name(self):
        if self.storageEngine:
            return self.storageEngine.name
        return None

    @property
    def node(self):
        if self.container:
            return self.container.node
        return None

    def _find_port(self, start_port=2000):
        while True:
            if j.sal.nettools.tcpPortConnectionTest(self.node.addr, start_port, timeout=2):
                start_port += 1
                continue
            return start_port

    def start(self, timeout=30):
        self.logger.debug("start %s", self)
        if not self.container.is_running():
            self.container.start()

        ip, port = self.storageEngine.bind.split(":")
        self.storageEngine.bind = '{}:{}'.format(ip, self._find_port(port))
        self.storageEngine.start(timeout=timeout)

    def stop(self, timeout=30):
        self.logger.debug("stop %s", self)
        self.storageEngine.stop(timeout=timeout)
        self.container.stop()

    def is_running(self):
        container = self.container.is_running()
        storageEngine, _ = self.storageEngine.is_running()
        return (container and storageEngine)

    def __str__(self):
        return "StorageServer <{}>".format(self.container.name)

    def __repr__(self):
        return str(self)


class StorageDashboard():
    def __init__(self, cluster, logger=None):
        self.cluster = cluster
        self.store = 'statsdb'


    def build_templating(self):
        templating = {
            "list": [],
            "rows": []
        }
        return templating

    def dashboard_template(self):
        return {
            "annotations": {
                "list": []
            },
            "editable": True,
            "gnetId": None,
            "graphTooltip": 0,
            "hideControls": False,
            "id": None,
            "links": [],
            "rows": [],
            "schemaVersion": 14,
            "style": "dark",
            "tags": [],
            "time": {
                "from": "now/d",
                "to": "now"
            },
            "timepicker": {
                "refresh_intervals": [
                    "5s",
                    "10s",
                    "30s",
                    "1m",
                    "5m",
                    "15m",
                    "30m",
                    "1h",
                    "2h",
                    "1d"
                ],
                "time_options": [
                    "5m",
                    "15m",
                    "1h",
                    "6h",
                    "12h",
                    "24h",
                    "2d",
                    "7d",
                    "30d"
                ]
            },
            "timezone": "",
            "title": self.cluster.name,
            "version": 8
        }

    def build_row(self, panel):
        template = {
            "collapse": False,
            "height": 295,
            "panels": [],
            "repeat": None,
            "repeatIteration": None,
            "repeatRowId": None,
            "showTitle": False,
            "title": "Dashboard Row",
            "titleSize": "h6"
        }
        template["panels"] += panel
        return template

    def build_panel(self, title, target, panel_id, unit):
        template = {
            "aliasColors": {},
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": self.store,
            "fill": 1,
            "id": panel_id,
            "legend": {
                "avg": False,
                "current": False,
                "max": False,
                "min": False,
                "show": True,
                "total": False,
                "values": False
            },
            "lines": True,
            "linewidth": 1,
            "links": [],
            "nullPointMode": "null",
            "percentage": False,
            "pointradius": 5,
            "points": False,
            "renderer": "flot",
            "seriesOverrides": [],
            "spaceLength": 10,
            "span": 6,
            "stack": True,
            "steppedLine": False,
            "targets": [],
            "thresholds": [],
            "timeFrom": None,
            "timeShift": None,
            "tooltip": {
                "shared": True,
                "sort": 0,
                "value_type": "individual"
            },
            "type": "graph",
            "xaxis": {
                "buckets": None,
                "mode": "time",
                "name": None,
                "show": True,
                "values": []
            },
            "yaxes": [
                {
                    "format": unit,
                    "label": None,
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                },
                {
                    "format": "short",
                    "label": None,
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                }
            ]
        }
        template["title"] = title
        template["targets"].append(target)
        return template

    def build_target(self, measurement, disks):
        template = {
            "alias": "$tag_node/$tag_id",
            "dsType": "influxdb",
            "groupBy": [
                {
                    "params": [
                        "$__interval"
                    ],
                    "type": "time"
                },
                {
                    "params": [
                        "node"
                    ],
                    "type": "tag"
                },
                {
                    "params": [
                        "id"
                    ],
                    "type": "tag"
                },
                {
                    "params": [
                        "none"
                    ],
                    "type": "fill"
                }
            ],
            "orderByTime": "ASC",
            "policy": "default",
            "rawQuery": False,
            "refId": "A",
            "resultFormat": "time_series",
            "select": [
                [
                    {
                        "params": [
                            "value"
                        ],
                        "type": "field"
                    },
                    {
                        "params": [],
                        "type": "mean"
                    }
                ]
            ],
            "tags": [
                {
                    "key": "type",
                    "operator": "=",
                    "value": "phys"
                }
            ]
        }
        template["measurement"] = measurement

        for idx, disk in enumerate(disks):
            tag = [
                {
                    "key": "node",
                    "operator": "=",
                    "value": disk.split("_")[0]
                },
                {
                    "condition": "AND",
                    "key": "id",
                    "operator": "=",
                    "value": disk.split("_")[1]
                }
            ]
            if idx == 0:
                tag[0]["condition"] = "AND"
            else:
                tag[0]["condition"] = "OR"
            template["tags"] += tag
        return template

    @property
    def template(self):
        AGGREGATED_CONFIG = {
            "Aggregated read IOPs": "disk.iops.read|m",
            "Aggregated write IOPs": "disk.iops.write|m",
            "Aggregated free size": "disk.size.free|m",
        }
        panel_id = 1
        disks = set()
        for sp in self.cluster.storage_pools:
            for devicePath in sp.devices:
                deviceName = os.path.basename(devicePath)
                disks.add("{}_{}".format(sp.node.name, deviceName))
        disks = list(disks)
        panels = []
        for title, measurement in AGGREGATED_CONFIG.items():
            if 'size' in title:
                partitions = [disk+'1' for disk in disks]
                target = self.build_target(measurement, partitions)
                panels.append(self.build_panel(title, target, panel_id, "decbytes"))
            else:
                target = self.build_target(measurement, disks)
                panels.append(self.build_panel(title, target, panel_id, "iops"))
            panel_id += 1

        for disk in disks:
            target = self.build_target("disk.iops.read|m", [disk])
            panels.append(self.build_panel("Read IOPs", target, panel_id, "iops"))
            panel_id += 1
            target = self.build_target("disk.iops.write|m", [disk])
            panels.append(self.build_panel("Write IOPs", target, panel_id, "iops"))
            panel_id += 1
            target = self.build_target("disk.size.free|m", [disk+'1'])
            panels.append(self.build_panel("Free size", target, panel_id, "decbytes"))
            panel_id += 1

        template = self.dashboard_template()
        for idx, panel in enumerate(panels):
            if idx % 2 == 0:
                row = self.build_row(panels[idx:idx+2])
                template["rows"].append(row)
        template = json.dumps(template)
        return template
