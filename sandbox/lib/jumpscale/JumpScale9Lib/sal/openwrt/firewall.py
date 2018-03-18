

from base import BaseService, BaseServiceSection
from js9 import j
JSBASE = j.application.jsbase_get_class()


class FirewallError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class Redirect(BaseServiceSection, JSBASE):
    EXPOSED_FIELDS = [
        'target',
        'src',
        'dest',
        'proto',
        'src_dport',
        'dest_ip',
        'dest_port',
        'name',
    ]

    def __init__(self):
        JSBASE.__init__(self)

    def __str__(self):
        return ('({proto}) {src_dport}:{src} -> '
                '{dest}:{dest_ip}:{dest_port}').format(
            proto=self.proto,
            src=self.src,
            src_dport=self.src_dport,
            dest=self.dest,
            dest_ip=self.dest_ip,
            dest_port=self.dest_port
        )

    def __repr__(self):
        return str(self)


class Rule(BaseServiceSection, JSBASE):
    EXPOSED_FIELDS = [
        'name',
        'proto',
        'family',
        'target',
        'src',
        'dest',
        'src_port',
        'dest_port',
    ]

    EXPOSED_BOOLEAN_FIELDS = [
        'enabled'
    ]

    def __init__(self):
        JSBASE.__init__(self)

    def __str__(self):
        return ('{name} {target}').format(
            name=self.name,
            target=self.target
        )

    def __repr__(self):
        return str(self)


class Firewall(BaseService, JSBASE):
    PACKAGE = 'firewall'

    def __init__(self):
        JSBASE.__init__(self)

    @property
    def zones(self):
        """
        Return names of all available zones to use in both redirects and
        firewall rules
        """
        return [s['name'] for s in self.package.find('zone')]

    @property
    def redirects(self):
        """
        List of all custom redirects (port forwarding)
        """
        return list(map(Redirect, self.package.find('redirect')))

    def addRedirect(self, name):
        """
        Add a new redirect (port forwarding)
        """
        red = Redirect(self.package.add('redirect'))
        red.name = name
        return red

    def removeRedirect(self, redirect):
        """
        Remove a redirect
        """
        self.package.remove(redirect.section)

    @property
    def rules(self):
        """
        All custom firewall rules
        """
        return list(map(Rule, self.package.find('rule')))

    def addRule(self, name):
        """
        Adds a new custom rule
        """
        rule = Rule(self.package.add('rule'))
        rule.name = name
        return rule

    def removeRule(self, rule):
        """
        Remove a custom firewall rule
        """
        self.package.remove(rule.section)

    def portOpen(self, name, src_port, dest_port, src='wan', dest='lan'):
        """
        Short cut for adding a firewall forwarding rule
        """
        rule = self.addRule(name)
        rule.target = 'ACCEPT'
        rule.src = src
        rule.dest = dest
        rule.src_port = src_port
        rule.dest_port = dest_port
        rule.enabled = True

        return rule

    def commit(self):
        self._wrt.commit(self.package)

        con = self._wrt.connection
        with settings(shell=self._wrt.WRT_SHELL,
                      abort_exception=FirewallError):
            # restart ftp
            con.run('/etc/init.d/firewall restart')
