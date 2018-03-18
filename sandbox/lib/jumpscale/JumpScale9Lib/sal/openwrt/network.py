

from base import BaseService, BaseServiceSection
from js9 import j
JSBASE = j.application.jsbase_get_class()


class NetworkError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class Interface(BaseServiceSection, JSBASE):
    EXPOSED_FIELDS = [
        'ifname',
        'type',
        'proto',
        'macaddr',

        # static
        'ipaddr',
        'netmask',
        'gateway',
        'broadcast',
        'dns',
        'dns_search'

        # dhcp
        'hostname',
    ]

    EXPOSED_BOOLEAN_FIELDS = [
        'enabled',
        'auto',

        # dhcp
        'broadcast'
    ]

    def __init__(self):
        JSBASE.__init__(self)

    def __str__(self):
        return '%s(ifname=%s)' % (self.section.name, self.ifname)

    def __repr__(self):
        return str(self)


class Network(BaseService, JSBASE):
    PACKAGE = 'network'

    def __init__(self, wrt=None):
        super(Network, self).__init__(wrt)
        JSBASE.__init__(self)
        self._nics = None

    @property
    def interfaces(self):
        return list(map(Interface, self.package.find('interface')))

    def addInterface(self, name):
        """
        Add UCI network 'config interface' section. This can be used
        to configure static ips on 'nics' or create bridges.
        """
        return Interface(self.package.add('interface', name))

    def removeInterface(self, interface):
        """
        Remove a UCI network 'config interface' section.
        """
        self.package.remove(interface.section)

    def find(self, ifname):
        """
        Return all interfaces that has this ifname
        """

        interfaces = []
        for inf in self.interfaces:
            if inf.ifname == ifname:
                interfaces.append(inf)

        return interfaces

    @property
    def nics(self):
        """
        All found netowrk devices (hw) and bridges
        """
        if self._nics is not None:
            return self._nics

        con = self._wrt.connection
        self._nics = []
        with settings(shell=self._wrt.WRT_SHELL):
            devices = con.run('ls --color=never -1 /sys/class/net/')
            for dev in devices.splitlines():
                dev = dev.strip()
                mac = con.run('cat /sys/class/net/%s/address' % dev).strip()
                self._nics.append((dev, mac))
        return self._nics

    def commit(self):
        self._wrt.commit(self.package)

        con = self._wrt.connection
        with settings(shell=self._wrt.WRT_SHELL, abort_exception=NetworkError):
            # restart networking
            con.run('/etc/init.d/network restart')
