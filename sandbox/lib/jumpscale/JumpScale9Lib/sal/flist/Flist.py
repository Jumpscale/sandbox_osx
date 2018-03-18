from js9 import j
import urllib.request
import tempfile
from urllib.parse import urlparse
import psutil

JSBASE = j.application.jsbase_get_class()


class Flist(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal.flist"
        JSBASE.__init__(self)

        self.FLISTDIR = j.sal.fs.joinPaths(j.dirs.VARDIR, "flists")
        self.CACHEDIR = j.sal.fs.joinPaths(j.dirs.VARDIR, "cache/flists/cache")
        self.MOUNTDIR = "/mnt/flists/"
        self.OVERLAYDIR = j.sal.fs.joinPaths(j.dirs.VARDIR, "cache/flists/overlay")


    def mount(self, name, flist, storageUrl = "ardb://hub.gig.tech:16379"):
        """
        mount 0-fs file system.

        :param name: name of the mounting file system
        :param flist: flist file to describe the structure of the file system, it can either be a local file or a remote one
        :param storageUrl: storage url of the actual files of the file system
        """
        self._verifyDirs([self.FLISTDIR, self.CACHEDIR, self.MOUNTDIR + name, self.OVERLAYDIR + name])

        if j.sal.fs.isMount(self.MOUNTDIR+name):
            return True

        flistFilePath = self._getFlistFileDestPath(flist)
        if not j.sal.fs.exists(flistFilePath):
            self._storeFlist(flist, flistFilePath)

        cmd = self._generateMountingCommand(name, flistFilePath, storageUrl)
        pm = j.tools.prefab.local.system.processmanager.get()
        pm.ensure(name, cmd)

    def list(self):
        """
        return the list of mounted file systems' names
        """
        return j.sal.fs.listDirsInDir(self.MOUNTDIR, dirNameOnly=True)

    def umount(self, name, destroy=False):
        """
        unmount 0-fs file system
        :param name: name of the file system to be unmounted
        :param destroy: if True, it will remove the file system directory
        """
        if not j.sal.fs.exists(self.MOUNTDIR+name):
            return True

        cmd = self._generateMountingCommand(name)
        processId = j.sal.process.getProcessPid(cmd)

        if processId != []:
            j.tools.executorLocal.execute("umount " + self.MOUNTDIR + name)
            proc = psutil.Process(processId[0])
            proc.wait(5)
            pm = j.tools.prefab.local.system.processmanager.get()
            pm.remove(name)

        if destroy:
            j.sal.fs.removeDirTree(self.MOUNTDIR + name)
            j.sal.fs.removeDirTree(self.OVERLAYDIR + name)
        return True

    def _generateMountingCommand(self, name, flistFilePath=None, storageUrl="ardb://hub.gig.tech:16379"):
        if flistFilePath is None:
            cmd = "g8ufs -backend {backend}"
        else:
            cmd = "g8ufs -backend {backend} -meta {flistFilePath} -storage-url {storage-url} -cache {cache} {mounting}"

        params = {'flistFilePath': flistFilePath,
                  'backend': j.sal.fs.joinPaths(self.OVERLAYDIR, name),
                  'cache': self.CACHEDIR,
                  'storage-url': storageUrl,
                  'mounting': j.sal.fs.joinPaths(self.MOUNTDIR, name), }
        cmd = cmd.format(**params)
        return cmd

    def _storeFlist(self, flist, flistFilePath):
        parsedUrl = urlparse(flist)
        if parsedUrl.scheme == "" or parsedUrl.scheme == "file://":
            j.tools.executorLocal.execute("cp " + flist + " " + flistFilePath)
        else:
            j.clients.http.getConnection().download(flist, flistFilePath)

    def _getFlistFileDestPath(self, flist):
        parsedUrl = urlparse(flist)
        if parsedUrl.scheme == "" or parsedUrl.scheme == "file://":
            flistMd5 = j.data.hash.md5(flist)
        else:
            flistMd5 = j.clients.http.getConnection().get(flist+".md5").read().decode()
            if flistMd5[-1] == "\n":
                flistMd5 = flistMd5[:-1]

        dest = self.FLISTDIR + flistMd5 + ".flist"
        return dest

    def _verifyDirs(self, dirs):
        for dir in dirs:
            j.sal.fs.createDir(dir)