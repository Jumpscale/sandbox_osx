from js9 import j

import packet
import time

JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
auth_token_ = ""
project_name = ""
"""


class PacketNet(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self._client = None
        self._plans = None
        self._facilities = None
        self._oses = None
        self._projects = None
        self._projectid = None
        self._devices = None
        self.projectname = self.config.data['project_name']

    @property
    def client(self):
        if not self._client:
            if not self.config.data['auth_token_']:
                raise RuntimeError(
                    "please configure your auth_token, do: 'js9_config configure -l j.clients.packetnet -i {}'".format(instance))
            self._client = packet.Manager(auth_token=self.config.data["auth_token_"])
        return self._client

    @property
    def projectid(self):
        if self._projectid is None:
            if self.projectname is not "":
                for item in self.projects:
                    if item.name == self.projectname:
                        self._projectid = item.id
                        return self._projectid
                raise RuntimeError(
                    "did not find project with name:%s" % self.projectname)
            else:
                res = [item[0] for key, item in self.getProjects().items()]
                if len(res) == 1:
                    self._projectid = res[0]
                else:
                    raise RuntimeError("found more than 1 project")
        return self._projectid

    @property
    def plans(self):
        if self._plans is None:
            self._plans = self.client.list_plans()
            self.logger.debug("plans:%s" % self._plans)
        return self._plans

    @property
    def facilities(self):
        if self._facilities is None:
            self._facilities = self.client.list_facilities()
            self.logger.debug("facilities:%s" % self._facilities)
        return self._facilities

    @property
    def operatingsystems(self):
        if self._oses is None:
            self._oses = self.client.list_operating_systems()
            self.logger.debug("operatingsystems:%s" % self._oses)
        return self._oses

    @property
    def projects(self):
        if self._projects is None:
            self._projects = self.client.list_projects()
            self.logger.debug("projects:%s" % self._projects)
        return self._projects

    @property
    def devices(self):
        if self._devices is None:
            self._devices = self.client.list_devices(self.projectid)
            self.logger.debug("devices:%s" % self._devices)
        return self._devices

    def getPlans(self):
        res = {}
        for plan in self.plans:
            res[plan.slug] = (plan.name, plan.specs)
        return res

    def getFacilities(self):
        res = {}
        for item in self.facilities:
            res[item.code] = item.name
        return res

    def getOperatingSystems(self):
        res = {}
        for item in self.operatingsystems:
            res[item.slug] = (item.name, item.distro,
                              item.version, item.provisionable_on)
        return res

    def getProjects(self):
        res = {}
        for item in self.projects:
            res[item.name] = (item.id, item.devices)
        return res

    def getDevices(self):
        res = {}
        for item in self.devices:
            res[item.hostname] = item
        return res

    def getDevice(self, name, id=None, die=False):
        if id is None:
            if name in [item for item in self.getDevices()]:
                return self.getDevices()[name]
            if die is False:
                return None
        else:
            return self.client.get_device(id)

        raise RuntimeError("could not find device:%s" % name)

    def removeDevice(self, name):
        res = self.getDevice(name)
        if res is not None:
            self._devices = None
            self.logger.debug("found machine, remove:%s" % name)
            res.delete()
        j.tools.nodemgr.delete(instance=name)

    def startDevice(self, hostname="removeMe", plan='baremetal_0', facility='ams1', os='ubuntu_17_04',
                    ipxeUrl=None, wait=True, remove=False, sshkey=""):
        """
        will delete if it exists when remove=True, otherwise will check if it exists, if yes will return device object
        if not will create

        example ipxeUrl = https://bootstrap.gig.tech/ipxe/zero-os-master-generic
        """
        self.logger.info("start device:%s plan:%s os:%s facility:%s wait:%s" % (hostname, plan, os, facility, wait))
        if ipxeUrl is None:
            zerotierId = ""
        else:
            zerotierId = ipxeUrl.split('/')[-1]
        return self._startDevice(hostname=hostname, plan=plan, facility=facility, os=os,
                                 wait=wait, remove=remove, ipxeUrl=ipxeUrl, zerotierId=zerotierId, always_pxe=False, sshkey=sshkey)

    def startZeroOS(self, hostname="removeMe", plan='baremetal_0', facility='ams1', zerotierId="", zerotierAPI="", wait=True, remove=False):
        """
        return (zero-os-client,pubIpAddress,zerotierIpAddress)
        """
        self.logger.info(
            "start device:%s plan:%s facility:%s zerotierId:%s wait:%s" % (hostname, plan, facility, zerotierId, wait)
        )
        if zerotierId.strip() == "" or zerotierId is None:
            raise RuntimeError("zerotierId needs to be specified")
        if zerotierAPI.strip() == "" or zerotierAPI is None:
            raise RuntimeError("zerotierAPI needs to be specified")
        ipxeUrl = "https://bootstrap.gig.tech/ipxe/master/%s" % zerotierId

        if params is not None:
            pstring = '%20'.join(params)
            ipxeUrl = ipxeUrl + '/' + pstring

        node = self._startDevice(hostname=hostname, plan=plan, facility=facility, os="",
                                 wait=wait, remove=remove, ipxeUrl=ipxeUrl, zerotierId=zerotierId, always_pxe=True)

        data = {'token_': zerotierAPI, 'networkID_': zerotierId}
        zerotierClient = j.clients.zerotier.get(self.instance, data=data)

        while True:
            try:
                member = zerotierClient.networkMemberGetFromIPPub(node.addr, networkId=zerotierId, online=True)
                ipaddr_priv = member["ipaddr_priv"][0]
                zerotierClient.memberAuthorize(zerotierNetworkId=zerotierId, ip_pub=node.addr)
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                self.logger.info("[-] %s" % e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                self.logger.error(
                    "[+] please authorize the server with the public ip %s in the zerotier network" % node.addr
                )
                time.sleep(1)

        self.logger.info("[+] zerotier IP: %s" % ipaddr_priv)
        data = {'host': ipaddr_priv, 'timeout': 10, 'port': 6379, 'password_': '', 'db': 0, 'ssl': True}
        zosclient = j.clients.zero_os.get(ipaddr_priv, data=data)
        return zosclient, node, ipaddr_priv

    def _startDevice(self, hostname="removeMe", plan='baremetal_0', facility='ams1',
                     os='ubuntu_17_04', wait=True, remove=True, ipxeUrl=None, zerotierId="", always_pxe=False,
                     sshkey=""):
        """
        will delete if it exists when remove=True, otherwise will check if it exists, if yes will return device object
        if not will create

        example ipxeUrl = https://bootstrap.gig.tech/ipxe/zero-os-master-generic
        """

        if ipxeUrl is None:
            ipxeUrl = ""
        if remove:
            self.removeDevice(hostname)

        if sshkey:
            sshkey = j.clients.sshkey.get(instance=sshkey)

        device = self.getDevice(hostname, die=False)
        if device is None:
            if sshkey:
                self.addSSHKey(sshkey, hostname)

            device = self.client.create_device(project_id=self.projectid,
                                               hostname=hostname,
                                               plan=plan,
                                               facility=facility,
                                               operating_system=os,
                                               ipxe_script_url=ipxeUrl,
                                               always_pxe=False)
            self._devices = None

        res = device.update()
        while res["state"] not in ["active"]:
            res = device.update()
            time.sleep(1)
            self.logger.debug(res["state"])

        ipaddr = [netinfo['address']
                  for netinfo in res["ip_addresses"] if netinfo['public'] and netinfo['address_family'] == 4]

        ipaddr = ipaddr[0]

        self.logger.info("ipaddress found = %s" % ipaddr)

        sshinstance = ""
        if zerotierId == "":
            j.sal.nettools.waitConnectionTest(ipaddr, 22, 60)

            if not sshkey:
                sshclient = j.clients.ssh.new(instance=hostname, addr=ipaddr)
            else:
                self.addSSHKey(sshkey, hostname)
                sshclient = j.clients.ssh.get(instance=sshkey.instance,
                                              data={'addr': ipaddr, 'login': 'root', 'sshkey': sshkey})
            sshclient.connect()

        conf = {}
        conf["facility"] = facility
        conf["netinfo"] = res["ip_addresses"]
        conf["plan"] = plan
        conf["hostname"] = hostname
        conf["project_id"] = self.projectid
        conf["os"] = os
        conf["ipxeUrl"] = ipxeUrl
        node = j.tools.nodemgr.set(name=hostname,
                                   sshclient=sshclient.instance,
                                   cat='packet',
                                   description='',
                                   selected=True,
                                   clienttype="j.clients.packetnet")

        j.tools.executor.reset()

        node.client = self
        node.pubconfig = conf

        return node

    def addSSHKey(self, sshkey, label):
        if j.data.types.string.check(sshkey):
            sshkey = j.clients.sshkey.get(instance=sshkey)

        ssh_keys = self.client.list_ssh_keys()
        for ssh_key in ssh_keys:
            if ssh_key.key == sshkey.pubkey:
                return ssh_key.owner

        self.client.create_ssh_key(label, sshkey.pubkey)


class PacketNetFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.packetnet"
        self.__imports__ = "packet"
        self.connections = {}
        JSConfigFactory.__init__(self, PacketNet)

    def install(self):
        j.sal.process.execute("pip3 install packet-python")

    def test(self):
        from IPython import embed
        embed(colors='Linux')
