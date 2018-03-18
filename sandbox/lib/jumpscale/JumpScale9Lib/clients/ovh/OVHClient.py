from js9 import j

try:
    import ovh
except:
    self.logger.warning("WARNING: ovh pip client not found please install do j.clients.ovh.install()")
    # OVHFactory().install()

import requests
import time

TEMPLATE = """
ipxeBase = "https://bootstrap.gig.tech/ipxe/master"
endpoint = "soyoustart-eu"
appkey_ = ""
appsecret_ = ""
consumerkey_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class OVHClient(JSConfigBase):
    """

    """

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE)
        c = self.config.data
        self.client = ovh.Client(
            endpoint=c["endpoint"],
            application_key=c["appkey_"],
            application_secret=c["appsecret_"],
            consumer_key=c["consumerkey_"],
        )

        # id = "ovhclient_%s" % c["consumerkey_"]
        self.ipxeBase = c["ipxeBase"]

    def ovh_id_check(self, ovh_id):
        if "ns302912" in ovh_id:
            raise RuntimeError("Cannot use server:%s" % ovh_id)

    def reset(self):
        """
        resets cache
        """
        self.cache.reset()

    def installationtemplates_get(self):
        """
        gets installation templates
        """
        def getData():
            self.logger.debug("get installationtemplates_get")
            return self.client.get('/dedicated/installationTemplate')
        return self.cache.get("installationtemplates_get", getData, expire=3600)

    def sshkeys_get(self):
        """
        lists ssh keys in server
        """
        def getData():
            self.logger.debug("get sshkeys")
            return self.client.get('/me/sshKey')
        return self.cache.get("sshKeys", getData)

    def sshkey_add(self, name, key):
        """ adds a ssh key to the server
        @param name: name of the new public SSH key
        @param key: ASCII encoded public SSH key to add
        """
        return self.client.post('/me/sshKey', keyName=name, key=key)

    def node_get(self, name):
        """
        get node by name
        """
        return j.tools.nodemgr.get(name, create=False)

    def servers_list(self):
        """
        list servers
        """
        def getData():
            self.logger.debug("get serversList")
            llist = self.client.get("/dedicated/server")
            llist = [item for item in llist if item.find("ns302912") == -1]
            return llist
        return self.cache.get("serversList", getData)

    def server_detail_get(self, name, reload=False):
        """
        get server details
        @param name: server name
        @param reload: if True the cache will be deleted and will the updated details
        """
        self.ovh_id_check(name)
        key = "server_detail_get_%s" % name
        if reload:
            self.cache.delete(key)

        def getData(name):
            return self.client.get("/dedicated/server/%s" % name)
        return self.cache.get(key, getData, name=name, expire=120)

    def server_install_status(self, name, reload=False):
        """
        get server install details
        @param name: server name
        @param reload: if True the cache will be deleted and will the updated details
        """
        self.ovh_id_check(name)
        key = "serverGetInstallStatus%s" % name
        if reload:
            self.cache.delete(key)

        def getData(name):
            self.logger.debug("get %s" % key)
            try:
                return self.client.get("/dedicated/server/%s/install/status" % name)
            except Exception as e:
                if "Server is not being installed or reinstalled at the moment" in str(e):
                    return "active"
                else:
                    raise e
        return self.cache.get(key, getData, name=name, expire=120)

    def servers_detail_get(self):
        """
        get details for all servers in self.servers_list()
        """
        res = []
        for item in self.servers_list():
            res.append((item, self.server_detail_get(item)))
        return res

    def servers_install_wait(self):
        nrInstalling = 1
        while nrInstalling > 0:
            nrInstalling = 0
            for item in self.servers_list():
                status = self.server_install_status(name=item, reload=True)
                key = "server_detail_get_%s" % item  # lets make sure server is out of cache too
                self.cache.delete(key)
                if status != "active":
                    self.logger.debug(item)
                    self.logger.debug(j.data.serializer.yaml.dumps(status))
                    self.logger.debug("-------------")
                    nrInstalling += 1
            time.sleep(2)
        self.details = {}
        self.logger.info("server install done")

    def server_install(self, name, ovh_id, installationTemplate="ubuntu1710-server_64", sshKeyName=None,
                       useDistribKernel=True, noRaid=True, hostname="", wait=True):
        """

        if sshKeyName == None, and there is only 1 loaded, then will take that key

        will return node_client

        """
        if name == "" or name is None:
            raise j.exceptions.Input(
                message="please specify name", level=1, source="", tags="", msgpub="")

        if ovh_id == "" or ovh_id is None:
            raise j.exceptions.Input(
                message="please specify ovh_id", level=1, source="", tags="", msgpub="")

        self.ovh_id_check(ovh_id)
        if installationTemplate not in self.installationtemplates_get():
            raise j.exceptions.Input(message="could not find install template:%s" %
                                     name, level=1, source="", tags="", msgpub="")

        if sshKeyName == None:
            items = j.clients.sshkey.list()
            # if len(items) != 1:
            #     raise RuntimeError(
            #         "sshkeyname needs to be specified or only 1 sshkey needs to be loaded")
            sshKeyName = items[0]
            sshKeyName = j.sal.fs.getBaseName(sshKeyName)

        if sshKeyName not in self.sshkeys_get():
            pubkey = j.clients.ssh.sshkey_pub_get(sshKeyName)
            self.sshkey_add(sshKeyName, pubkey)

        if hostname == "":
            hostname = name

        details = {}
        details["installationTemplate"] = installationTemplate
        details["useDistribKernel"] = useDistribKernel
        details["noRaid"] = noRaid
        details["customHostname"] = hostname
        details["sshKeyName"] = sshKeyName

        # make sure cache for this server is gone
        key = "server_detail_get_%s" % name
        self.cache.delete(key)

        try:
            self.client.post("/dedicated/server/%s/install/start" %
                             ovh_id, details=details, templateName=installationTemplate)
        except Exception as e:
            if "A reinstallation is already in todo" in str(e):
                self.logger.debug("%s:%s" % (name, e))
                pass
            else:
                raise e

        if wait:
            self.servers_install_wait()

        if name == "":
            self.details = {}
        else:
            if name in self.details:
                self.details.pop(name)

        conf = self.server_detail_get(ovh_id)
        ipaddr = conf['ip']
        port = 22

        node = j.tools.nodemgr.set(name, ipaddr, port, sshclient=sshKeyName, cat="ovh", clienttype="j.clients.ovh")

        j.tools.executor.reset()

        return node

    def boot_image_pxe_list(self):
        """
        Lists iPXE scripts installed on the account
        """
        return self.client.get("/me/ipxeScript")

    def boot_image_pxe_get(self, name):
        """
        Returns contents of the iPXE script name given in parameter
        """
        return self.client.get("/me/ipxeScript/%s" % name)

    def boot_image_pxe_delete(self, name):
        """
        Delete a iPXE script boot entry
        Note: this require DELETE account capability
        """
        return self.client.delete("/me/ipxeScript/%s" % name)

    def boot_image_pxe_set(self, name, script, description=""):
        """
        Set a new iPXE boot script bootloader
        ipxe: should contains a dictionary with:
          - description: a description which will be displayed on the summary page
          - name: a name which will identify the iPXE script entry
          - script: the iPXE script which will be executed during the boot
        """
        dd = {}
        dd["name"] = name
        dd["script"] = script
        dd["description"] = description

        return self.client.post("/me/ipxeScript", **dd)

    def boot_image_pxe_available(self, name):
        """
        Checkk if an iPXE boot script name already exists
        """
        existing = self.boot_image_pxe_list()

        for item in existing:
            if item == name:
                return True

        return None

    def _bootloader_set(self, target, bootid):
        self.logger.info("[+] bootloader selected: %s" % bootid)

        payload = {"bootId": int(bootid)}
        self.client.put("/dedicated/server/%s" % target, **payload)

        return True

    def bootloader_set(self, target, name):
        """
        Set and apply an iPXE boot script to a remote server
        - target: need to be a OVH server hostname
        - name: need to be an existing iPXE script name
        """
        bootlist = self.client.get(
            "/dedicated/server/%s/boot?bootType=ipxeCustomerScript" % target)
        # checked = None

        for bootid in bootlist:
            data = self.client.get(
                "/dedicated/server/%s/boot/%s" % (target, bootid))
            if data['kernel'] == name:
                return self._bootloader_set(target, bootid)

        return False

    def server_reboot(self, name):
        """
        Reboot a server
        - target: need to be a OVH server hostname
        """
        self.ovh_id_check(name)
        return self.client.post("/dedicated/server/%s/reboot" % name)

    #
    # custom builder
    #
    def _zos_build(self, url):
        """
        Internal use.
        This build an OVH adapted iPXE script based on an official bootstrap URL
        """
        # strip trailing flash
        url = url.rstrip('/')
        self.logger.info("zero hub url:%s" % url)
        # downloading original ipxe script
        try:
            script = requests.get(url)
        except Exception as e:
            msg = "ERROR: zerohub server does not respond\nError:\n%s\n" % e
            raise(msg)
        if script.status_code != 200:
            raise RuntimeError("Invalid script URL")

        # going unsecure, because ovh
        fixed = script.text.replace(
            'https://bootstrap.', 'http://unsecure.bootstrap.')

        # setting name and description according to the url
        fields = url.split('/')

        if len(fields) == 7:
            # branch name, zerotier network, arguments
            description = "Zero-OS: %s (%s, %s)" % (
                fields[4], fields[5], fields[6])
            name = "zero-os-%s-%s,%s" % (fields[4], fields[5], fields[6])

        elif len(fields) == 6:
            # branch name, zerotier network, no arguments
            description = "Zero-OS: %s (%s, no arguments)" % (
                fields[4], fields[5])
            name = "zero-os-%s-%s" % (fields[4], fields[5])

        else:
            # branch name, no zerotier, no arguments
            description = "Zero-OS: %s (no zerotier, no arguments)" % fields[4]
            name = "zero-os-%s" % fields[4]

        return {'description': description, 'name': name, 'script': fixed}

    def zero_os_boot(self, target, zerotierNetworkID):
        """
        Configure a node to use Zero-OS iPXE kernel
        - target: need to be an OVH server hostname
        - zerotierNetworkID: network to be used in zerotier
        """
        self.ovh_id_check(target)
        url = "%s/%s" % (self.ipxeBase, zerotierNetworkID)
        ipxe = self._zos_build(url)

        self.logger.info("[+] description: %s" % ipxe['description'])
        self.logger.info("[+] boot loader: %s" % ipxe['name'])

        if not self.boot_image_pxe_available(ipxe['name']):
            self.logger.info("[+] installing the bootloader")
            self.boot_image_pxe_set(ipxe['name'], ipxe['script'], ipxe['description'])
        self.bootloader_set(target, ipxe['name'])
        return self.server_reboot(target)

    def task_get(self, target, taskId):
        """
        get a task
        @param target: target name
        @param taskId: taskId
        """
        return self.client.get("/dedicated/server/%s/task/%s" % (target, taskId))

    def server_wait_reboot(self, target, taskId):
        current = ""

        while True:
            status = self.task_get(target, taskId)

            if status['status'] != current:
                current = status['status']
                self.logger.info("[+] rebooting %s: %s" % (target, current))

            if status['status'] == 'done':
                return True

            time.sleep(1)
