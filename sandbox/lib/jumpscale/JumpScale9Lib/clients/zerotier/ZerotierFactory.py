from js9 import j

import zerotier
import requests
import json


JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
token_ = ""
networkID_ = ""
"""
JSBASE = j.application.jsbase_get_class()


class ZerotierClientInteral(JSBASE):
    def __init__(self, apikey):
        JSBASE.__init__(self)
        self.apikey = apikey
        self.apibase = "https://my.zerotier.com/api"

    def request(self, path, data=None):
        if data is None:
            return requests.get(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey})

        else:
            return requests.post(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey}, json=data)

    def delete(self, path):
        return requests.delete(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey})

    def status(self):
        return self.request("/status").json()

    def user(self, id):
        return self.request("/user/%s" % id).json()

    def networks(self):
        return self.request("/network").json()

    # def network_create(self, name):
    #     data = {
    #         "config": {
    #             "name": name,
    #             "rules": [{"ruleNo": 1, "action": "accept"}],
    #             "v4AssignMode": "zt",
    #             "routes": [{"target": "10.147.17.0/24", "via": None, "flags": 0, "metric": 0}],
    #             "ipAssignmentPools": [{"ipRangeStart": "10.147.17.1", "ipRangeEnd": "10.147.17.254"}]
    #         }
    #     }

    #     return self.request("/network", data).json()

    def network_delete(self, id):
        return self.delete("/network/%s" % id)


class ZerotierClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        super().__init__(instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)

        if not self.config.data['token_']:
            self.configure()
        if not self.config.data['token_']:
            raise RuntimeError("Missing auth token in config instance {}".format(instance))
        self.client = zerotier.client.Client()
        self.client.set_auth_header("Bearer " + self.config.data['token_'])
        self._client = ZerotierClientInteral(self.config.data['token_'])

    def memberAuthorize(self, zerotierNetworkId, ip_pub):
        res = self.client.network.listMembers(id=zerotierNetworkId).json()
        members = [item for item in res if item['physicalAddress'] == ip_pub]
        if not members:
            raise RuntimeError('no such memeber as %s' % zerotierNetworkId)
        member = members[0]
        if member['config']["authorized"] is False:
            id = member["nodeId"]
            member['config']['authorized'] = True
            data = json.dumps(member)
            self._client.request("/network/%s/member/%s" % (zerotierNetworkId, id), member)
            self.logger.info('[+] authorized %s on %s' % (member['physicalAddress'], zerotierNetworkId))

    def networksGet(self):
        """
        returns [(id,name,onlinecount)]
        """
        res0 = self.client.network.listNetworks().json()
        res = []
        for item in res0:
            res.append((item["id"], item["config"]["name"],
                        item["onlineMemberCount"]))
        return res

    def networkMembersGet(self, networkId, online=True):
        res = self.client.network.listMembers(id=networkId).json()
        result = []
        for item in res:
            res2 = {}
            res2["authorized"] = item["config"]["authorized"]
            # item["creationTime"]
            res2["name"] = item["name"]
            res2["id"] = item["id"]
            if online and item["online"] is False:
                continue
            res2["online"] = item["online"]
            res2["lastOnlineHR"] = j.data.time.epoch2HRDateTime(
                item["lastOnline"] / 1000)
            res2["lastOnline"] = item["lastOnline"]
            res2["ipaddr_priv"] = item["config"]["ipAssignments"]
            res2["ipaddr_pub"] = item["physicalAddress"].split(
                "/")[0] if item["physicalAddress"] else None
            result.append(res2)
        return result

    def networkMemberGetFromIPPub(self, ip_pub, networkId, online=True):
        res = self.networkMembersGet(networkId, online)

        res = [item for item in res if item['ipaddr_pub'] == ip_pub]

        if len(res) is 0:
            raise RuntimeError(
                "Did not find network member with ipaddr:%s" % ip_pub)

        return res[0]


class ZerotierFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.zerotier"
        self.__imports__ = "zerotier"
        self.connections = {}
        JSConfigFactory.__init__(self, ZerotierClient)
