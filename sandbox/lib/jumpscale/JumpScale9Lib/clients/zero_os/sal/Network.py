import netaddr
from js9 import j


def combine(ip1, ip2, mask):
    """
    >>> combine('10.0.3.11', '192.168.1.10', 24)
    '10.0.3.10'
    """
    iip1 = netaddr.IPNetwork('{}/{}'.format(ip1, mask))
    iip2 = netaddr.IPNetwork('{}/{}'.format(ip2, mask))
    ires = iip1.network + int(iip2.ip & (~ int(iip2.netmask)))
    net = netaddr.IPNetwork(ires)
    net.prefixlen = mask
    return net


class Network():

    def __init__(self, node):
        self.node = node

    @property
    def client(self):
        return self.node.client

    def get_management_info(self):
        import netaddr

        def get_nic_ip(nics, name):
            for nic in nics:
                if nic['name'] == name:
                    for ip in nic['addrs']:
                        return netaddr.IPNetwork(ip['addr'])
                    return

        defaultgwdev = self.client.bash("ip route | grep default | awk '{print $5}'").get().stdout.strip()
        nics = self.client.info.nic()
        mgmtaddr = None
        if defaultgwdev:
            ipgwdev = get_nic_ip(nics, defaultgwdev)
            if ipgwdev:
                mgmtaddr = str(ipgwdev.ip)
        if not mgmtaddr:
            mgmtaddr = self.node.addr

        return mgmtaddr

    def get_addresses(self, network):
        mgmtaddr = self.get_management_info()
        return {
            'storageaddr': combine(str(network.ip), mgmtaddr, network.prefixlen),
            'vxaddr': combine('10.240.0.0', mgmtaddr, network.prefixlen),
        }

    def get_free_nics(self):
        nics = self.client.info.nic()
        nics.sort(key=lambda nic: nic['speed'])
        availablenics = {}
        for nic in nics:
            # skip all interface that have an ipv4 address
            if any(netaddr.IPNetwork(addr['addr']).version == 4 for addr in nic['addrs'] if 'addr' in addr):
                continue
            if nic['speed'] == 0:
                continue
            availablenics.setdefault(nic['speed'], []).append(nic['name'])
        return sorted(availablenics.items())

    def reload_driver(self, driver):
        self.node.client.system('modprobe -r {}'.format(driver)).get()
        devs = {link['name'] for link in self.node.client.ip.link.list()}
        self.node.client.system('modprobe {}'.format(driver)).get()
        # brings linsk up
        alldevs = {link['name'] for link in self.node.client.ip.link.list()}
        driverdevs = alldevs - devs
        for link in driverdevs:
            self.node.client.ip.link.up(link)

        # wait max 10 seconds for these nics to become up (speed available)
        now = time.time()
        while time.time() - 10 < now:
            for nic in self.node.client.info.nic():
                if nic['speed'] and nic['name'] in driverdevs:
                    driverdevs.remove(nic['name'])
            if not driverdevs:
                break
            time.sleep(1)

    def configure(self, cidr, vlan_tag, ovs_container_name,  bonded=False):
        container_sal = self.node.containers.get(ovs_container_name)
        if not container_sal.is_running():
            container_sal.start()

        nicmap = {nic['name']: nic for nic in self.node.client.info.nic()}
        # freenics = ([1000, ['eth0']], [100, ['eth1']])
        freenics = self.node.network.get_free_nics()
        if not freenics:
            raise j.exceptions.RuntimeError("Could not find available nic")

        network = netaddr.IPNetwork(cidr)
        addresses = self.get_addresses(network)

        interfaces = None
        if not bonded:
            interfaces = [freenics[0][1][0]]
        else:
            for speed, interfaces in freenics:
                if len(interfaces) >= 2:
                    interfaces = interfaces[:2]
                    break
            else:
                raise j.exceptions.RuntimeError("Could not find two equal available nics")

        if 'backplane' not in nicmap:
            container_sal.client.json('ovs.bridge-add', {"bridge": "backplane"})
            if not bonded:
                container_sal.client.json('ovs.port-add', {"bridge": "backplane", "port": interfaces[0], "vlan": 0})
            else:
                container_sal.client.json('ovs.bond-add', {"bridge": "backplane",
                                                           "port": "bond0",
                                                           "links": interfaces,
                                                           "lacp": True,
                                                           "mode": "balance-tcp"})
            # TODO: this need to be turned into 0-os primitives
            self.node.client.ip.addr.add('backplane', str(addresses['storageaddr']))
            for interface in interfaces:
                self.node.client.system('ip link set dev {} mtu 2000'.format(interface)).get()
                self.node.client.ip.link.up(interface)
            self.node.client.ip.link.up('backplane')

        if 'vxbackend' not in nicmap:
            container_sal.client.json('ovs.vlan-ensure', {'master': 'backplane', 'vlan': vlan_tag, 'name': 'vxbackend'})
            # TODO: this need to be turned into 0-os primitives
            self.node.client.ip.addr.add('vxbackend', str(addresses['vxaddr']))
            self.node.client.system('ip link set dev vxbackend mtu 2000').get()
            self.node.client.ip.link.up('vxbackend')
