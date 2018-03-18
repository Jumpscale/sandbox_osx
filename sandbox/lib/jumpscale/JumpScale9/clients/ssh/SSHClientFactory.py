
import os
import threading

from js9 import j

from .SSHClient import SSHClient

JSConfigBase = j.tools.configmanager.base_class_configs


class SSHClientFactory(JSConfigBase):

    _lock = threading.Lock()
    cache = {}

    def __init__(self):
        self.__jslocation__ = "j.clients.ssh"
        self.__imports__ = "paramiko"
        JSConfigBase.__init__(self, SSHClient)

    def new(self, addr, port=22, instance="", keyname="", timeout=5, die=True, login="root", passwd="",
            stdout=True, allow_agent=False, addr_priv="", port_priv=22):
        """
        @PARAM instance is the name used for the sshclient instance name

        e.g. j.clients.ssh.new("192.168.8.8",instance="mytest",login="root",passwd="rooter")
        """
        if not instance:
            instance = addr.replace(".", "-") + "-%s" % port
        data = {}
        data["port"] = port
        data["addr"] = addr
        data["sshkey"] = keyname
        data["timeout"] = timeout
        data["stdout"] = stdout
        data["login"] = login
        data["passwd_"] = passwd
        data["allow_agent"] = allow_agent
        data["addr_priv"] = addr_priv
        data["port_priv"] = port_priv

        # if key in self.cache and usecache:
        #     try:
        #         usecache = not (self.cache[key]._client is None)
        #     except j.exceptions.RuntimeError:
        #         usecache = False
        cl = self.get(instance=instance, data=data, die=die)
        return cl

    def get(self, instance="main", data={}, create=True, die=True, interactive=False):
        """
        Get an instance of the SSHClient

        @param instance: instance name to get. If an instance is already loaded in memory, return it
        @data data: dictionary of data use to configure the instance
        """
        instance = instance.replace(".", "-")  # allows address to be used
        if not create and instance not in self.list():
            if die:
                raise RuntimeError("could not find instance:%s" % (instance))
            else:
                return None

        return SSHClient(instance=instance, data=data, parent=self, interactive=interactive)

    def reset(self):
        """
        Close and clear cached ssh clients
        """
        with self._lock:
            for _, client in self.cache.items():
                client.close()
            self.cache = {}
        j.tools.executor.reset()

    def close(self):
        with self._lock:
            for _, client in self.cache.items():
                client.close()

    def test_packetnet(self, reset=False):
        '''
        js9 'j.clients.ssh.test_packetnet()'
        '''

        # will get your main connection to packet.net make sure has been configured
        packetnetcl = j.clients.packetnet.get("test")

        loginname = j.tools.myconfig.config.data["login_name"]
        if loginname == "":
            raise RuntimeError("please configure your login name, do:\n'js9_config configure -l j.tools.myconfig'")
        hostname = '%s-test' % loginname

        # make sure we have an sshkey, will be without passphrase like this
        skey = j.clients.sshkey.get(instance="test10")
        skey.generate()
        skey.load()
        assert skey.is_loaded()  # check is loaded

        node = packetnetcl.startDevice(hostname=hostname, plan='baremetal_1', facility='ams1',
                                       os='ubuntu_17_10', ipxeUrl=None, wait=True, remove=reset, sshkey="test10")

        node.prefab.core.run('which curl')
        packetnetcl.removeDevice(hostname)
        self.logger.info("test successful and device removed")
