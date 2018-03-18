#!/usr/bin/env python
from .Container import Container

from js9 import j
import os
import docker
import time
from urllib import parse
import copy
JSBASE = j.application.jsbase_get_class()


class Docker(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal.docker"
        self.__imports__ = "docker"
        JSBASE.__init__(self)
        self._basepath = "/storage/docker"
        self._prefix = ""
        self._containers = None
        self._names = []

        if 'DOCKER_HOST' not in os.environ or os.environ['DOCKER_HOST'] == "":
            self.base_url = 'unix://var/run/docker.sock'
        else:
            self.base_url = os.environ['DOCKER_HOST']
        self.client = docker.APIClient(base_url=self.base_url)


    def _node_set(self, name, sshclient):
        j.tools.nodemgr.set(name, sshclient=sshclient.instance, selected=False,
                            cat="docker", clienttype="j.sal.docker", description="deployment on docker")

    @property
    def containers(self):
        self._containers = []
        for obj in self.client.containers():
            self._containers.append(Container(obj,self.client))
        return self._containers

    @property
    def docker_host(self):
        u = parse.urlparse(self.base_url)
        if u.scheme == 'unix':
            return 'localhost'
        else:
            return u.hostname

    @property
    def containerNamesRunning(self):
        """
        List all running containers names
        """
        res = []
        for container in self.containers:
            if container.isRunning():
                res.append(container.name)
        return res
    
    @property
    def weaveIsActive(self):
        # TODO: suppot weave
        return False

    @property
    def containerNames(self):
        """
        List all containers names
        """
        res = []
        for container in self.containers:
            res.append(container.name)
        return res

    @property
    def containersRunning(self):
        """
        List of all running container objects
        """
        res = []
        for container in self.containers:
            if container.isRunning():
                res.append(container)
        return res

    def exists(self, name):
        return name in self.containerNames

    @property
    def basepath(self):
        self._basepath = '/mnt/data/docker'
        # TODO: needs to fetch values out of hrd
        # if not self._basepath:
        #     if j.application.config.exists('docker.basepath'):
        #         self._basepath = j.application.config.get('docker.basepath')
        #     else:
        #         self._basepath="/mnt/vmstor/docker" #btrfs subvol create
        return self._basepath

    def _getChildren(self, pid, children):
        process = j.sal.process.getProcessObject(pid)
        children.append(process)
        for child in process.get_children():
            children = self._getChildren(child.pid, children)
        return children

    def _get_rootpath(self, name):
        rootpath = j.sal.fs.joinPaths(
            self.basepath, '%s%s' % (self._prefix, name), 'rootfs')
        return rootpath

    def _getMachinePath(self, machinename, append=""):
        if machinename == "":
            raise j.exceptions.RuntimeError("Cannot be empty")
        base = j.sal.fs.joinPaths(self.basepath, '%s%s' %
                                  (self._prefix, machinename))
        if append != "":
            base = j.sal.fs.joinPaths(base, append)
        return base

    def status(self):
        """
        return list docker with some info
        returns [[name, image, sshport, status]]

        """

        res = []
        for item in self.containers:
            res.append([item.name,item.image ,
                        item.ssh_port,item.status])

        return res

    def ps(self):
        """
        return detailed info
        """

        return self.client.containers()

    def get(self, name, die=True):
        """
        Get a container object by name
        @param name string: container name
        """
        for container in self.containers:
            if container.name == name:
                return container
        if die:
            raise j.exceptions.RuntimeError(
                "Container with name %s doesn't exists" % name)
        else:
            return None

    def get_container_by_id(self, id, die=True):
        """
        Get a container object by name
        @param name string: container name
        """
        for container in self.containers:
            if container.id == id:
                return container
        if die:
            raise j.exceptions.RuntimeError(
                "Container with name %s doesn't exists" % name)
        else:
            return None

    def exportRsync(self, name, backupname, key="pub"):
        raise j.exceptions.RuntimeError("not implemented")
        self.removeRedundantFiles(name)
        ipaddr = j.core.state.configGet("jssync.addr")
        path = self._getMachinePath(name)
        if not j.sal.fs.exists(path):
            raise j.exceptions.RuntimeError("cannot find machine:%s" % path)
        if backupname[-1] != "/":
            backupname += "/"
        if path[-1] != "/":
            path += "/"
        cmd = "rsync -a %s %s::upload/%s/images/%s --delete-after --modify-window=60 --compress --stats  --progress --exclude '.Trash*'" % (
            path, ipaddr, key, backupname)
        j.sal.process.executeWithoutPipe(cmd)

    # def removeRedundantFiles(self,name):
    #     raise j.exceptions.RuntimeError("not implemented")
    #     basepath=self._getMachinePath(name)
    #     j.sal.fs.removeIrrelevantFiles(basepath,followSymlinks=False)

    #     toremove="%s/rootfs/var/cache/apt/archives/"%basepath
    #     j.sal.fs.removeDirTree(toremove)

    def importRsync(self, backupname, name, basename="", key="pub"):
        """
        @param basename is the name of a start of a machine locally, will be used as basis and then the source will be synced over it
        """
        raise j.exceptions.RuntimeError("not implemented")
        ipaddr = j.core.state.configGet("jssync.addr")
        path = self._getMachinePath(name)

        self.btrfsSubvolNew(name)

        # j.sal.fs.createDir(path)

        if backupname[-1] != "/":
            backupname += "/"
        if path[-1] != "/":
            path += "/"

        if basename != "":
            basepath = self._getMachinePath(basename)
            if basepath[-1] != "/":
                basepath += "/"
            if not j.sal.fs.exists(basepath):
                raise j.exceptions.RuntimeError(
                    "cannot find base machine:%s" % basepath)
            cmd = "rsync -av -v %s %s --delete-after --modify-window=60 --size-only --compress --stats  --progress" % (
                basepath, path)
            self.logger.info(cmd)
            j.sal.process.executeWithoutPipe(cmd)

        cmd = "rsync -av -v %s::download/%s/images/%s %s --delete-after --modify-window=60 --compress --stats  --progress" % (
            ipaddr, key, backupname, path)
        self.logger.info(cmd)
        j.sal.process.executeWithoutPipe(cmd)

    def exportTgz(self, name, backupname):
        raise j.exceptions.RuntimeError("not implemented")
        self.removeRedundantFiles(name)
        path = self._getMachinePath(name)
        bpath = j.sal.fs.joinPaths(self.basepath, "backups")
        if not j.sal.fs.exists(path):
            raise j.exceptions.RuntimeError("cannot find machine:%s" % path)
        j.sal.fs.createDir(bpath)
        bpath = j.sal.fs.joinPaths(bpath, "%s.tgz" % backupname)
        cmd = "cd %s;tar Szcf %s ." % (path, bpath)
        j.sal.process.executeWithoutPipe(cmd)
        return bpath

    def importTgz(self, backupname, name):
        raise j.exceptions.RuntimeError("not implemented")
        path = self._getMachinePath(name)
        bpath = j.sal.fs.joinPaths(
            self.basepath, "backups", "%s.tgz" % backupname)
        if not j.sal.fs.exists(bpath):
            raise j.exceptions.RuntimeError(
                "cannot find import path:%s" % bpath)
        j.sal.fs.createDir(path)

        cmd = "cd %s;tar xzvf %s -C ." % (path, bpath)
        j.sal.process.executeWithoutPipe(cmd)

    def _init_aysfs(self, fs, dockname):
        if fs.isUnique():
            if not fs.isRunning():
                self.logger.info('starting unique aysfs: %s' % fs.getName())
                fs.start()

            else:
                self.logger.info(
                    'skipping aysfs: %s (unique running)' % fs.getName())

        else:
            fs.setName('%s-%s' % (dockname, fs.getName()))
            if fs.isRunning():
                fs.stop()

            self.logger.info('starting aysfs: %s' % fs.getName())
            fs.start()

    def create(
            self,
            name="",
            ports="",
            vols="",
            volsro="",
            stdout=True,
            base="jumpscale/ubuntu1604",
            nameserver=["8.8.8.8"],
            replace=True,
            cpu=None,
            mem=0,
            ssh=True,
            myinit=True,
            sharecode=False,
            sshkeyname="",
            sshpubkey="",
            setrootrndpasswd=True,
            rootpasswd="",
            jumpscalebranch="master",
            aysfs=[],
            detach=False,
            privileged=False,
            getIfExists=True,
            command=""):
        """
        Creates a new container.

        @param ports in format as follows  "22:8022 80:8080"  the first arg e.g. 22 is the port in the container
        @param vols in format as follows "/var/insidemachine:/var/inhost # /var/1:/var/1 # ..."   '#' is separator
        @param sshkeyname : use ssh-agent (can even do remote through ssh -A) and then specify key you want to use in docker
        """
        if ssh is True and myinit is False:
            raise ValueError("SSH can't be enabled without myinit.")
        # check there is weave
        #

        name = name.lower().strip()
        self.logger.info(("create:%s" % name))

        running = [item.name for item in self.containersRunning]

        if not replace:
            if name in self.containerNamesRunning:
                if getIfExists:
                    return self.get(name=name)
                else:
                    j.events.opserror_critical(
                        "Cannot create machine with name %s, because it does already exists.")
        else:
            if self.exists(name):
                self.logger.info("remove existing container %s" % name)
                container = self.get(name)
                if container:
                    container.destroy()

        if vols is None:
            vols = ""
        if volsro is None:
            volsro = ""
        if ports is None:
            ports = ""

        if mem is not None:
            if mem > 0:
                mem = int(mem) * 1024
            elif mem <= 0:
                mem = None

        portsdict = {}
        if len(ports) > 0:
            items = ports.split(" ")
            for item in items:
                key, val = item.split(":", 1)
                ss = key.split("/")
                if len(ss) == 2:
                    portsdict[tuple(ss)] = val
                else:
                    portsdict[int(key)] = val

        if ssh:
            if 22 not in portsdict:
                for port in range(9022, 9190):
                    if not j.sal.nettools.tcpPortConnectionTest(self.docker_host, port):
                        portsdict[22] = port
                        self.logger.info(("ssh port will be on:%s" % port))
                        break

        volsdict = {}
        if len(vols) > 0:
            items = vols.split("#")
            for item in items:
                key, val = item.split(":", 1)
                volsdict[str(key).strip()] = str(val).strip()

        if sharecode and j.sal.fs.exists(path="/opt/code"):
            self.logger.info("share jumpscale code enable")
            if "/opt/code" not in volsdict:
                volsdict["/opt/code"] = "/opt/code"

        for fs in aysfs:
            self._init_aysfs(fs, name)
            mounts = fs.getPrefixs()

            for inp, out in mounts.items():
                while not j.sal.fs.exists(inp):
                    time.sleep(0.1)

                volsdict[out] = inp

        volsdictro = {}
        if len(volsro) > 0:
            items = volsro.split("#")
            for item in items:
                key, val = item.split(":", 1)
                volsdictro[str(key).strip()] = str(val).strip()

        self.logger.info("Volumes map:")
        for src1, dest1 in list(volsdict.items()):
            self.logger.info(" %-20s %s" % (src1, dest1))

        binds = {}
        binds2 = []
        volskeys = []  # is location in docker

        for key, path in list(volsdict.items()):
            # j.sal.fs.createDir(path)  # create the path on hostname
            binds[path] = {"bind": key, "ro": False}
            binds2.append("%s:%s" % (path, key))
            volskeys.append(key)

        for key, path in list(volsdictro.items()):
            # j.sal.fs.createDir(path)  # create the path on hostname
            binds[path] = {"bind": key, "ro": True}
            volskeys.append(key)

        if base not in self.getImages():
            self.logger.info("download docker image %s" % base)
            self.pull(base)

        if base.startswith("jumpscale/ubuntu1604") or myinit is True:
            command = "sh -c \"mkdir -p /var/run/screen;chmod 777 /var/run/screen; /var/run/screen;exec >/dev/tty 2>/dev/tty </dev/tty && /sbin/my_init -- /usr/bin/screen -s bash\""
            command = "sh -c \" /sbin/my_init -- bash -l\""
        else:
            command = None

        self.logger.info(("install docker with name '%s'" % name))

        if vols != "":
            self.logger.info("Volumes")
            self.logger.info(volskeys)
            self.logger.info(binds)

        hostname = None if self.weaveIsActive else name.replace('_', '-')

        if self.weaveIsActive:
            nameserver = None

        for k, v in portsdict.items():
            if isinstance(k, tuple) and len(k) == 2:
                portsdict["%s/%s" % (k[0], k[1])] = v
                portsdict.pop(k)

        host_config = self.client.create_host_config(
            binds=binds2,
            port_bindings=portsdict,
            lxc_conf=None,
            publish_all_ports=False,
            links=None,
            privileged=privileged,
            dns=nameserver,
            dns_search=None,
            volumes_from=None,
            network_mode=None)
        res = self.client.create_container(
            image=base,
            command=command,
            hostname=hostname,
            user="root",
            detach=detach,
            stdin_open=False,
            tty=True,
            ports=list(
                portsdict.keys()),
            environment=None,
            volumes=volskeys,
            network_disabled=False,
            name=name,
            entrypoint=None,
            working_dir=None,
            domainname=None,
            host_config=host_config,
            mac_address=None,
            labels=None,
            stop_signal=None,
            networking_config=None, 
            healthcheck=None, 
            stop_timeout=None, 
            runtime=None)
        if res["Warnings"] is not None:
            raise j.exceptions.RuntimeError(
                "Could not create docker, res:'%s'" % res)

        id = res["Id"]

        res = self.client.start(container=id)

        container = self.get_container_by_id(id)

        if ssh:
            if setrootrndpasswd:
                if rootpasswd is None or rootpasswd == '':
                    rootpasswd = 'gig1234'

            container.authorizeSSH(sshkeyname=sshkeyname, password=rootpasswd)

            # Make sure docker is ready for executor
            end_time = time.time() + 60
            while time.time() < end_time:
                rc, _, _ = container.executor.execute('ls /', die=False, showout=False)
                if rc:
                    time.sleep(0.1)
                break

            self._node_set(name, container.sshclient)
        return container

    def getImages(self):
        images = []
        for item in self.client.images():
            if item['RepoTags'] is None:
                continue
            tags = str(item['RepoTags'][0])
            tags = tags.replace(":latest", "")
            images.append(tags)
        return images

    def removeImages(self, tag="<none>:<none>"):
        """
        Delete a certain Docker image using tag
        """
        for item in self.client.images():
            if tag in item["RepoTags"]:
                self.client.remove_image(item["Id"])

    def ping(self):

        try:
            self.client.ping()
        except Exception as e:
            return False
        return True

    def destroyAll(self, removeimages=False):
        """
        Destroy all containers.
        @param removeimages bool: to remove all images.
        """
        for container in self.containers:
            if "weave" in container.name:
                continue
            container.destroy()

        if removeimages:
            self.removeImages()

    def _destroyAllKill(self):

        if self.ping():

            for container in self.containers:
                container.destroy()

            self.removeImages()

        j.sal.process.execute("systemctl stop docker")

        if j.sal.fs.exists(path="/var/lib/docker/btrfs/subvolumes"):
            j.sal.btrfs.subvolumesDelete('/var/lib/docker/btrfs/subvolumes')

        if j.sal.fs.exists(path="/var/lib/docker/volumes"):
            for item in j.sal.fs.listDirsInDir("/var/lib/docker/volumes"):
                j.sal.fs.removeDirTree(item)

    def removeDocker(self):
        self._destroyAllKill()

        rc, out, _ = j.sal.process.execute("mount")
        mountpoints = []
        for line in out.split("\n"):
            if line.find("type btrfs") != -1:
                mountpoint = line.split("on ")[1].split("type")[0].strip()
                mountpoints.append(mountpoint)

        for mountpoint in mountpoints:
            j.sal.btrfs.subvolumesDelete(mountpoint, "/docker/")

        j.sal.btrfs.subvolumesDelete("/storage", "docker")

        j.sal.process.execute("apt-get remove docker-engine -y")
        # j.sal.process.execute("rm -rf /var/lib/docker")

        j.sal.fs.removeDirTree("/var/lib/docker")

    def reInstallDocker(self):
        """
        ReInstall docker on your system
        """
        self.removeDocker()

        j.tools.prefab.local.docker.install(force=True)

        self.init()

    def pull(self, imagename):
        """
        pull a certain image.
        @param imagename string: image
        """
        self.client.import_image_from_image(imagename)

    def push(self, image, output=True):
        """
        image: str, name of the image
        output: print progress as it pushes
        """
        client = self.client
        previous_timeout = client.timeout
        client.timeout = 36000
        out = []
        for l in client.push(image, stream=True):
            line = j.data.serializer.json.loads(l)
            id = line['id'] if 'id' in line else ''
            s = "%s " % id
            if 'status' in line:
                s += line['status']
            if 'progress' in line:
                detail = line['progressDetail']
                progress = line['progress']
                s += " %50s " % progress
            if 'error' in line:
                message = line['errorDetail']['message']
                raise j.exceptions.RuntimeError(message)
            if output:
                self.logger.info(s)
            out.append(s)

        client.timeout = previous_timeout

        return "\n".join(out)

    def build(self, path, tag, output=True, force=False):
        """
        path: path of the directory that contains the docker file
        tag: tag to give to the image. e.g: 'jumpscale/myimage'
        output: print output as it builds

        return: strint containing the stdout
        """
        # TODO: implement force
        out = []
        if force:
            nocache = True
        for l in self.client.build(path=path, tag=tag, nocache=nocache):
            line = j.data.serializer.json.loads(l)
            if 'stream' in line:
                line = line['stream'].strip()
                if output:
                    self.logger.info(line)
                out.append(line)

        return "\n".join(out)

    # class DockerExecObj:

    #     def __init__(self, name):
    #         self.name = name
    #         self.id = "docker:%s" % name

    #     def execute(self, cmds, die=True, checkok=None, async=False, showout=True, timeout=0, env={}):
    #         return self._prefabDockerHost.core.run("docker exec %s  %s" % (self.name, cmds))


    # def init(self):

    #     j.sal.process.execute("systemctl stop docker")

    #     d = j.sal.disklayout.findDisk(mountpoint="/storage")
    #     if d is not None:
    #         # we found a disk, lets make sure its in fstab
    #         d.setAutoMount()
    #         dockerpath = "%s/docker" % d.mountpoint
    #         dockerpath = dockerpath.replace("//", '/')
    #         if dockerpath not in j.sal.btrfs.subvolumeList(d.mountpoint):
    #             # have to create the dockerpath
    #             j.sal.btrfs.subvolumeCreate(dockerpath)
    #     # j.sal.fs.createDir("/storage/docker")
    #     j.sal.fs.copyDirTree("/var/lib/docker", dockerpath)
    #     j.sal.fs.symlink("/storage/docker", "/var/lib/docker",
    #                      overwriteTarget=True)

    #     j.sal.process.execute("systemctl start docker")

    # @property
    # def weaveIsActive(self):
    #     return bool()

    # @property
    # def weavesocket(self):
    #     if self._weaveSocket is None:
    #         if not j.tools.prefab.local.core.command_check('weave'):
    #             self.logger.warning("weave not found, do not forget to start if installed.")
    #             self._weaveSocket = ""
    #         else:

    #             # rc, self._weaveSocket = j.sal.process.__execute("eval $(weave env) &&
    #             # echo $DOCKER_HOST", die=False)                rc, self._weaveSocket =
    #             # j.sal.process.__execute("eval $(weave env) && echo $DOCKER_HOST",
    #             # die=False) echo $DOCKER_HOST", die=False)
    #             # FIXME : j.sal.process execute treats eval $(weave en) as a single executable
    #             # WILL SET IT TO j.sal.process.execute for now.
    #             rc, self._weaveSocket, _ = j.sal.process.execute("eval $(weave env)")
    #             if rc > 0:
    #                 self.logger.warning("weave not found, do not forget to start if installed.")
    #                 self._weaveSocket = ""

    #             self._weaveSocket = self._weaveSocket.strip()

    #     return self._weaveSocket

    # def weaveInstall(self, ufw=False):
    #     j.tools.prefab.local.systemservices.weave.install(start=True)
    #     if ufw:
    #         j.tools.prefab.local.systemservices.ufw.allowIncoming(6783)
    #         j.tools.prefab.local.systemservices.ufw.allowIncoming(6783, protocol="udp")

    # def connectRemoteTCP(self, base_url):
    #     self.base_url = base_url
    #     self.client = docker.Client(base_url=weavesocket)

    # def _execute(self, command):
    #     env = os.environ.copy()
    #     env.pop('PYTHONPATH', None)
    #     (exitcode, stdout, stderr) = j.sal.process.run(
    #         command, showOutput=False, captureOutput=True, stopOnError=False, env=env)
    #     if exitcode != 0:
    #         raise j.exceptions.RuntimeError(
    #             "Failed to execute %s: Error: %s, %s" % (command, stdout, stderr))
    #     return stdout

    #
    # def copy(self, name, src, dest):
    #     rndd = j.data.idgenerator.generateRandomInt(10, 1000000)
    #     temp = "/var/docker/%s/%s" % (name, rndd)
    #     j.sal.fs.createDir(temp)
    #     source_name = j.sal.fs.getBaseName(src)
    #     if j.sal.fs.isDir(src):
    #         j.sal.fs.copyDirTree(src, j.sal.fs.joinPaths(temp, source_name))
    #     else:
    #         j.sal.fs.copyFile(src, j.sal.fs.joinPaths(temp, source_name))
    #
    #     ddir = j.sal.fs.getDirName(dest)
    #     cmd = "mkdir -p %s" % (ddir)
    #     self.run(name, cmd)
    #
    #     cmd = "cp -r /var/jumpscale/%s/%s %s" % (rndd, source_name, dest)
    #     self.run(name, cmd)
    #     j.sal.fs.remove(temp)