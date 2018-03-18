from js9 import j

import time

from paramiko.ssh_exception import BadAuthenticationType
from .Authorizables import Authorizables
from .Machine import Machine


class Space(Authorizables):

    def __init__(self, account, model):
        Authorizables.__init__(self)

        self.account = account
        self.client = account.client
        self._model = model
        self._machines = {}
        self.id = model["id"]

    def externalnetwork_add(self, name, subnet, gateway, startip, endip, gid, vlan):
        self.client.api.cloudbroker.iaas.addExternalNetwork(cloudspaceId=self.id,
                                                            name=name,
                                                            subnet=subnet,
                                                            getway=gateway,
                                                            startip=startip,
                                                            endip=endip,
                                                            gid=gid,
                                                            vlan=vlan)
        self.refresh()

    def save(self):
        self.client.api.cloudapi.cloudspaces.update(cloudspaceId=self.model['id'],
                                                    name=self.model['name'],
                                                    maxMemoryCapacity=self.model.get(
                                                        'maxMemoryCapacity'),
                                                    maxVDiskCapacity=self.model.get(
                                                        'maxVDiskCapacity'),
                                                    maxCPUCapacity=self.model.get(
                                                        'maxCPUCapacity'),
                                                    maxNASCapacity=self.model.get(
                                                        'maxNASCapacity'),
                                                    maxNetworkOptTransfer=self.model.get(
                                                        'maxNetworkOptTransfer'),
                                                    maxNetworkPeerTransfer=self.model.get(
                                                        'maxNetworkPeerTransfer'),
                                                    maxNumPublicIP=self.model.get(
                                                        'maxNumPublicIP')
                                                    )
        self.refresh()

    @property
    def model(self):

        timeout = j.data.time.epoch + 20

        while self._model["status"] == 'DEPLOYING' and j.data.time.epoch < timeout:
            self.logger.info(
                "Cloudspace is still deploying, checking again in 2 second"
            )
            time.sleep(1)
            self.refresh()

        while not self._model['publicipaddress'] and j.data.time.epoch < timeout:
            self.logger.info(
                "Cloudspace still in deployment, waiting for pub ip addr."
            )
            time.sleep(1)
            self.refresh()

        if j.data.time.epoch > timeout:
            raise RuntimeError("timeout on getting space info from %s" % self)

        return self._model

    @property
    def ipaddr_pub(self):
        return self.model['publicipaddress']

    @property
    def machines(self):
        ovc_machines = self.client.api.cloudapi.machines.list(cloudspaceId=self.id)
        machines = dict()
        for machine in ovc_machines:
            machines[machine['name']] = Machine(self, machine)
        return machines

    def _addUser(self, username, right):
        self.client.api.cloudapi.cloudspaces.addUser(
            cloudspaceId=self.id, userId=username, accesstype=right)

    def _deleteUser(self, username):
        self.client.api.cloudapi.cloudspaces.deleteUser(
            cloudspaceId=self.id, userId=username, recursivedelete=True)

    def _updateUser(self, username, right):
        self.client.api.cloudapi.cloudspaces.updateUser(
            cloudspaceId=self.id, userId=username, accesstype=right)

    def enable(self, reason):
        """
        Will enable the cloud space.
        : param reason: string: The reason why the cloud space should be enabled.
        """
        self.client.api.cloudapi.cloudspaces.enable(
            cloudspaceId=self.id, reason=reason)

    def disable(self, reason):
        """
        Will disable the cloud space.
        : param reason: string: The reason why the cloud space should be disabled.
        """
        self.client.api.cloudapi.cloudspaces.disable(
            cloudspaceId=self.id, reason=reason)

    def refresh(self):
        self.cache.reset()
        cloudspaces = self.client.api.cloudapi.cloudspaces.list()
        for cloudspace in cloudspaces:
            if cloudspace['id'] == self.id:
                self._model = cloudspace
                break
        else:
            raise j.exceptions.RuntimeError("Cloud space has been deleted")

    def machine_get(
            self,
            name,
            create=False,
            sshkeyname="",
            memsize=2,
            vcpus=1,
            disksize=10,
            datadisks=[],
            image="Ubuntu 16.04 x64",
            sizeId=None,
            stackId=None,
            reset=False,
            managed_private=False):
        """
        Returns the virtual machine with given name, and in case it doesn't exist yet creates the machine if the create argument is set to True.

        Args:
            - name: (required) name of the virtual machine to lookup or create if it doesn't exist yet, e.g. "My first VM"
            - create (defaults to False): if set to true the machine is created in case it doesn't exist yet
            - sshkeyname (only required for creating new machine): name of the private key loaded by ssh-agent that will get copied into authorized_keys
            - memsize (defaults to 2): memory size in MB or in GB, e.g. 4096
            - vcpus (defaults to 1): number of virtual CPU cores; value is ignored in versions prior to 3.x, use sizeId in order to set the number of virtual CPU cores
            - disksize (default to 10): boot disk size in MB
            - datadisks (optional): list of data disks sizes in GB, e.g. [20, 20, 50]
            - image (defaults to "Ubuntu 16.04 x6"): name of the OS image to load
            - sizeId (optional): overrides the value set for memsize, denotes the type or "size" of the virtual machine, actually sets the number of virtual CPU cores and amount of memory, see the sizes property of the cloud space for the sizes available in the cloud space
            - stackId (optional): identifies the grid node on which to create the virtual machine, if nothing specified (recommended) OpenvCloud will decide where to create the virtual machine
            - reset: if True remove if exists
            - managed_private: if set to true, the access to the VM will be done using the private IP of the vm. Which means the client needs to be execute from a machine that can access the private
                               network of the cloudspace
                               if False, use the public IP of the cloudspace to access the VM. It will create a port forward to be able to access the VM

        Raises: RuntimeError if machine doesn't exist, and create argument was set to False (default)
        """

        if name in self.machines and reset:
            self.machines[name].delete()

        if name not in self.machines:
            if create is True:
                machine = self.machine_create(name=name,
                                              sshkeyname=sshkeyname,
                                              memsize=memsize,
                                              vcpus=vcpus,
                                              disksize=disksize,
                                              datadisks=datadisks,
                                              image=image,
                                              sizeId=sizeId,
                                              stackId=stackId,
                                              managed_private=managed_private)
                machine.new = True
                self.machines[name] = machine
            else:
                raise RuntimeError("Cannot find machine:%s" % name)

        machine = self.machines[name]
        if not managed_private:
            self._node_set(machine.name, machine.sshclient)
        else:
            self._node_set(machine.name+'_private', machine.sshclient_private)

        machine.new = False

        return machine

    def _node_set(self, name, sshclient):
        j.tools.nodemgr.set(name, sshclient=sshclient.instance, selected=False,
                            cat="openvcloud", clienttype="j.clients.openvcloud", description="deployment in openvcloud")

    def machines_delete(self):
        """
        Deletes all machines in the cloud space.
        """
        for key, machine in self.machines.items():
            machine.delete()
            j.tools.nodemgr.delete(key)
        self.refresh()

    def machine_create(
        self,
        name,
        sshkeyname=None,
        memsize=2,
        vcpus=None,
        disksize=10,
        datadisks=[],
        image="Ubuntu 16.04 x64",
        sizeId=None,
        stackId=None,
        description=None,
        managed_private=False
    ):
        """
        Creates a new virtual machine.

        Args:
            - name (required): name of the virtual machine, e.g. "MyFirstVM"
            - sshkeyname (required): name of instance of sshkey's which need to be pre-configured
            - memsize (defaults to 2): memory size in MB or in GB, e.g. 4096
            - vcpus (defaults to 1): number of virtual CPU cores; value is ignored in versions prior to 3.x, use sizeId in order to set the number of virtual CPU cores
            - disksize (default to 10): boot disk size in MB
            - datadisks (optional): list of data disks sizes in GB, e.g. [20, 20, 50]
            - image (defaults to "Ubuntu 16.04 x6"): name of the OS image to load
            - sizeId (optional): overrides the value set for memsize, denotes the type or "size" of the virtual machine, actually sets the number of virtual CPU cores and amount of memory, see the sizes property of the cloud space for the sizes available in the cloud space
            - stackId (optional): identifies the grid node on which to create the virtual machine, if nothing specified (recommended) OpenvCloud will decide where to create the virtual machine
            - description (optional): machine description
            - managed_private: if set to true, the access to the VM will be done using the private IP of the vm. Which means the client needs to be execute from a machine that can access the private
                               network of the cloudspace
                               if False, use the public IP of the cloudspace to access the VM. It will create a port forward to be able to access the VM

        Raises:
            - RuntimeError if machine with given name already exists.
            - RuntimeError if machine name contains spaces
            - RuntimeError if machine name contains underscores
        """
        self.logger.debug("Create machine:%s:%s:%s" %
                          (name, image, sshkeyname))
        if ' ' in name:
            raise RuntimeError('Name cannot contain spaces')
        if '_' in name:
            raise RuntimeError('Name cannot contain underscores (_)')

        imageId = self.image_find_id(image)
        if sizeId is None:
            sizeId = self.size_find_id(memsize, vcpus)
        if name in self.machines:
            raise j.exceptions.RuntimeError(
                "Name is not unique, already exists in %s" % self)
        self.logger.info("Cloud space ID:%s name:%s size:%s image:%s disksize:%s" %
                         (self.id, name, sizeId, imageId, disksize))

        if description is None:
            description = ""

        if sshkeyname and "sshkeyname:" not in description:
            description += "\nsshkeyname: %s" % sshkeyname

        if stackId:
            self.client.api.cloudbroker.machine.createOnStack(
                cloudspaceId=self.id,
                name=name,
                sizeId=sizeId,
                imageId=imageId,
                disksize=disksize,
                datadisks=datadisks,
                stackid=stackId,
                description=description)
            machine = self.machines[name]
            machine.new = True
        else:
            self.client.api.cloudapi.machines.create(cloudspaceId=self.id,
                                                     name=name,
                                                     sizeId=sizeId,
                                                     imageId=imageId,
                                                     disksize=disksize,
                                                     datadisks=datadisks,
                                                     description=description)
            machine = self.machines[name]
            machine.new = True

        self.logger.info("machine created.")

        machine = self.machines[name]
        if not managed_private:
            machine.portforward_create(None, 22)

        if sshkeyname:
            if not managed_private:
                machine.authorizeSSH(sshkeyname=sshkeyname)
            else:
                machine.authorizeSSH_private(sshkeyname=sshkeyname)
        else:
            raise RuntimeError("needs to be implemented, no sshkeyname given")

        if not managed_private:
            machine.prefab.core.hostname = name  # make sure hostname is set
            self._node_set(machine.name, machine.sshclient)
        else:
            machine.prefab_private.core.hostname = name  # make sure hostname is set
            self._node_set(machine.name+'_private', machine.sshclient_private)

        return machine

    @property
    def portforwards(self):
        return self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.id)

    def portforward_exists(self, publicIp, publicport, protocol):
        for pf in self.portforwards:
            if pf['publicIp'] == publicIp and int(pf['publicPort']) == int(publicport) and pf['protocol'] == protocol:
                return True
        return False

    def size_find_id(self, memory=None, vcpus=None):
        if memory < 100:
            memory = memory * 1024  # prob given in GB

        sizes = [(item["memory"], item) for item in self.sizes]
        sizes.sort(key=lambda size: size[0], reverse=True)
        for size, sizeinfo in sizes:
            if memory > size / 1.1:
                if vcpus and vcpus != sizeinfo['vcpus']:
                    continue
                return sizeinfo['id']

        raise j.exceptions.RuntimeError(
            "did not find memory size:%s, or found with different vcpus" % memory)

    @property
    def sizes(self):
        return self.client.api.cloudapi.sizes.list(cloudspaceId=self.id)

    def image_find_id(self, name):
        name = name.lower()

        for image in self.images:
            imageNameFound = image["name"].lower()
            if imageNameFound.find(name) != -1:
                return image["id"]
        images = [item["name"].lower() for item in self.images]
        raise j.exceptions.RuntimeError(
            "did not find image:%s\nPossible Images:\n%s\n" % (name, images))

    @property
    def images(self):
        return self.client.api.cloudapi.images.list(cloudspaceId=self.id, accountId=self.account.id)

    def delete(self):
        self.client.api.cloudapi.cloudspaces.delete(cloudspaceId=self.id)

    # def execute_routeros_script(self, script):
    #     self.client.api.cloudapi.cloudspaces.executeRouterOSScript(
    #         cloudspaceId=self.id, script=script)

    def __repr__(self):
        return "space: %s (%s)" % (self.model["name"], self.id)

    __str__ = __repr__
