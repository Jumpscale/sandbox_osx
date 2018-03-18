import json

from js9 import j

from . import typchk


class BridgeManager():
    _bridge_create_chk = typchk.Checker({
        'name': str,
        'hwaddr': typchk.Or(str, typchk.IsNone()),
        'network': {
            'mode': typchk.Or(typchk.Enum('static', 'dnsmasq'), typchk.IsNone()),
            'nat': bool,
            'settings': typchk.Map(str, str),
        }
    })

    _bridge_delete_chk = typchk.Checker({
        'name': str,
    })

    def __init__(self, client):
        self._client = client

    def create(self, name, hwaddr=None, network=None, nat=False, settings={}):
        """
        Create a bridge with the given name, hwaddr and networking setup
        :param name: name of the bridge (must be unique), 15 characters or less, and not equal to "default".
        :param hwaddr: MAC address of the bridge. If none, a one will be created for u
        :param network: Networking mode, options are none, static, and dnsmasq
        :param nat: If true, SNAT will be enabled on this bridge. (IF and ONLY IF an IP is set on the bridge
                    via the settings, otherwise flag will be ignored) (the cidr attribute of either static, or dnsmasq modes)
        :param settings: Networking setting, depending on the selected mode.
                        none:
                            no settings, bridge won't get any ip settings
                        static:
                            settings={'cidr': 'ip/net'}
                            bridge will get assigned the given IP address
                        dnsmasq:
                            settings={'cidr': 'ip/net', 'start': 'ip', 'end': 'ip'}
                            bridge will get assigned the ip in cidr
                            and each running container that is attached to this IP will get
                            IP from the start/end range. Netmask of the range is the netmask
                            part of the provided cidr.
                            if nat is true, SNAT rules will be automatically added in the firewall.
        """
        args = {
            'name': name,
            'hwaddr': hwaddr,
            'network': {
                'mode': network,
                'nat': nat,
                'settings': settings,
            }
        }

        self._bridge_create_chk.check(args)
        self.logger.info("bridge.create:%s" % args)
        response = self._client.raw('bridge.create', args)

        result = response.get()
        if result.state != 'SUCCESS':
            raise RuntimeError('failed to create bridge %s' % result.data)

        return json.loads(result.data)

    def list(self):
        """
        List all available bridges
        :return: list of bridge names
        """
        self.logger.info("bridge.list")
        response = self._client.raw('bridge.list', {})

        result = response.get()
        if result.state != 'SUCCESS':
            raise RuntimeError('failed to list bridges: %s' % result.data)

        return json.loads(result.data)

    def delete(self, bridge):
        """
        Delete a bridge by name

        :param bridge: bridge name
        :return:
        """
        args = {
            'name': bridge,
        }

        self._bridge_delete_chk.check(args)
        self.logger.info("bridge.delete:%s" % bridge)
        response = self._client.raw('bridge.delete', args)

        result = response.get()
        if result.state != 'SUCCESS':
            raise RuntimeError('failed to list delete: %s' % result.data)
