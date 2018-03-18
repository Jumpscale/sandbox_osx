from js9 import j
import os
import errno
import stat
JSBASE = j.application.jsbase_get_class()

def _is_block(file):
    try:
        st = os.stat(file)
    except OSError as err:
        if err.errno == errno.ENOENT:
            return False
        raise
    return stat.S_ISBLK(st.st_mode)


def get_open_blks(pid):
    retlist = set()
    files = os.listdir("/proc/%s/fd" % pid)
    hit_enoent = False
    for fd in files:
        file = "/proc/%s/fd/%s" % (pid, fd)
        if os.path.islink(file):
            try:
                file = os.readlink(file)
            except OSError as err:
                if err.errno == errno.ENOENT:
                    hit_enoent = True
                    continue
                raise
            else:
                if file.startswith('/') and _is_block(file):
                    retlist.add(int(fd))
    if hit_enoent:
        # raise NSP if the process disappeared on us
        os.stat('/proc/%s' % pid)
    return retlist


class Disk(JSBASE):
    """
    identifies a disk in the grid
    """

    def __init__(self):
        self.id = 0
        self.path = ""
        self.size = ""
        self.free = ""
        self.ssd = False
        self.fs = ""
        self.mounted = False
        self.mountpoint = ""
        self.model = ""
        self.description = ""
        self.type = []
        JSBASE.__init__(self)

    def __str__(self):
        return "%s %s %s free:%s ssd:%s fs:%s model:%s id:%s" % (
            self.path, self.mountpoint, self.size, self.free, self.ssd, self.fs, self.model, self.id)

    __repr__ = __str__


class Diskmanager(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal.diskmanager"
        self._parted = None
        JSBASE.__init__(self)

    @property
    def parted(self):
        if self._parted is None:
            try:
                import parted
            except BaseException:
                j.sal.ubuntu.apt_install("python3-parted")
                import parted

            # patch self.parted
            _orig_getAllDevices = parted.getAllDevices

            def _patchedGetAllDevices():
                pid = os.getpid()
                fds = get_open_blks(pid)
                try:
                    return _orig_getAllDevices()
                finally:
                    afds = get_open_blks(pid)
                    for fd in afds.difference(fds):
                        os.close(fd)

            parted.getAllDevices = _patchedGetAllDevices
            self._parted = parted
        return self._parted

    def partitionAdd(self, disk, free, align=None, length=None, fs_type=None, type=None):
        """
        Add a partition on a disk
        """
        if type is None:
            type = self.parted.PARTITION_NORMAL
        start = free.start
        if length:
            end = start + length - 1
        else:
            end = free.end
            length = free.end - start + 1

        if not align:
            align = disk.partitionAlignment.intersect(
                disk.device.optimumAlignment)

        if not align.isAligned(free, start):
            start = align.alignNearest(free, start)

        end_align = self.parted.Alignment(
            offset=align.offset - 1, grainSize=align.grainSize)
        if not end_align.isAligned(free, end):
            end = end_align.alignNearest(free, end)

        geometry = self.parted.Geometry(disk.device, start=start, end=end)
        if fs_type:
            fs = self.parted.FileSystem(type=fs_type, geometry=geometry)
        else:
            fs = None
        partition = self.parted.Partition(
            disk, type=type, geometry=geometry, fs=fs)
        constraint = self.parted.Constraint(exactGeom=partition.geometry)
        disk.addPartition(partition, constraint)
        return partition

    def diskGetFreeRegions(self, disk, align):
        """Get a filtered list of free regions, excluding the gaps due to partition alignment"""
        regions = disk.getFreeSpaceRegions()
        new_regions = []
        for region in regions:
            if region.length > align.grainSize:
                new_regions.append(region)
        return new_regions

    def _kib_to_sectors(self, device, kib):
        return self.parted.sizeToSectors(kib, 'KiB', device.sectorSize)

    def mirrorsFind(self):
        cmd = "cat /proc/mdstat"
        rcode, out, _ = j.sal.process.execute(cmd)
        return out

    def partitionsFind(self, mounted=None, ttype=None, ssd=None, prefix="sd", minsize=5, maxsize=5000, devbusy=None,
                       initialize=False, forceinitialize=False):
        """
        looks for disks which are know to be data disks & are formatted ext4

        @param ttype is a string variable defining the format type
        @param minsize is an int variable indicating the minimum partition size and defaulted to 5
        @param mazsize is an int variable indicating the minimum partition size and defaulted to 5000
        @param ssd if None then ssd and other
        :return [[$partpath,$size,$free,$ssd]]
        """
        import psutil
        result = []
        mounteddevices = psutil.disk_partitions()

        def getpsutilpart(partname):
            for part in mounteddevices:
                if part.device == partname:
                    return part
            return None

        for dev in self.parted.getAllDevices():
            path = dev.path
            #ssize = dev.sectorSize;
            # size = (geom[0] * geom[1] * geom[2] * ssize) / 1000 / 1000 / 1000;
            # size2=dev.getSize()

            if devbusy is None or dev.busy == devbusy:
                if path.startswith("/dev/%s" % prefix):
                    try:
                        disk = self.parted.Disk(dev)
                        partitions = disk.partitions
                    except self.parted.DiskLabelException:
                        partitions = list()
                    for partition in partitions:
                        disko = Disk()
                        disko.model = dev.model
                        disko.path = partition.path if disk.type != 'loop' else disk.device.path
                        disko.size = round(partition.getSize(unit="mb"), 2)
                        disko.free = 0
                        self.logger.debug(("partition:%s %s" % (disko.path, disko.size)))
                        try:
                            fs = self.parted.probeFileSystem(
                                partition.geometry)
                        except BaseException:
                            fs = "unknown"

                        disko.fs = fs
                        partfound = getpsutilpart(disko.path)
                        mountpoint = None
                        if partfound is None and mounted != True:
                            mountpoint = "/mnt/tmp"
                            cmd = "mount %s /mnt/tmp" % partition.path
                            rcode, output, err = j.sal.process.execute(
                                cmd, ignoreErrorOutput=False, die=False,)
                            if rcode != 0:
                                # mount did not work
                                mountpoint is None

                            disko.mountpoint = None
                            disko.mounted = False
                        elif partfound:
                            mountpoint = partfound.mountpoint
                            disko.mountpoint = mountpoint
                            disko.mounted = True

                        pathssdcheck = "/sys/block/%s/queue/rotational" % dev.path.replace(
                            "/dev/", "").strip()
                        if j.sal.fs.exists(pathssdcheck):
                            ssd0 = int(j.sal.fs.fileGetContents(
                                pathssdcheck)) == 0
                        else:
                            ssd0 = False
                        disko.ssd = ssd0
                        result.append(disko)

                        if mountpoint is not None:
                            self.logger.debug(("mountpoint:%s" % mountpoint))
                            size, used, free, percent = psutil.disk_usage(
                                mountpoint)
                            disko.free = disko.size * float(1 - percent / 100)

                            size = disko.size / 1024
                            disko.free = int(disko.free)

                            if (ttype is None or fs == ttype) and size > minsize and (
                                    maxsize is None or size < maxsize):
                                if ssd is None or disko.ssd == ssd:
                                    hrdpath = "%s/disk.hrd" % mountpoint

                                    if j.sal.fs.exists(hrdpath):
                                        hrd = j.data.hrd.get(hrdpath)
                                        partnr = hrd.getInt("diskinfo.partnr")
                                        if partnr == 0 or forceinitialize:
                                            j.sal.fs.remove(hrdpath)

                                    if not j.sal.fs.exists(hrdpath) and initialize:
                                        C = """
                                        diskinfo.partnr=
                                        diskinfo.type=
                                        diskinfo.epoch=
                                        diskinfo.description=
                                        """
                                        j.sal.fs.writeFile(
                                            filename=hrdpath, contents=C)
                                        hrd = j.data.hrd.get(hrdpath)
                                        hrd.set("diskinfo.description", j.tools.console.askString(
                                            "please give description for disk"))
                                        hrd.set("diskinfo.type", ",".join(j.tools.console.askChoiceMultiple(
                                            ["BOOT", "CACHE", "TMP", "DATA", "OTHER"])))
                                        hrd.set("diskinfo.epoch",
                                                j.data.time.getTimeEpoch())

                                        # TODO (*4*) ---> get connection from
                                        # AYS, lets discuss this does not seem
                                        # right any longer
                                        j.data.models_system.connect2mongo()

                                        disk = j.data.models_system.Disk()
                                        for key, val in list(disko.__dict__.items()):
                                            disk.__dict__[key] = val

                                        disk.description = hrd.get(
                                            "diskinfo.description")
                                        disk.type = hrd.get(
                                            "diskinfo.type").split(",")
                                        disk.type.sort()

                                        disk.save()
                                        diskid = disk.guid
                                        hrd.set("diskinfo.partnr", diskid)
                                    if j.sal.fs.exists(hrdpath):
                                        # hrd=j.data.hrd.get(hrdpath)
                                        disko.id = hrd.get("diskinfo.partnr")
                                        disko.type = hrd.get(
                                            "diskinfo.type").split(",")
                                        disko.type.sort()
                                        disko.description = hrd.get(
                                            "diskinfo.description")
                                        self.logger.debug(("found disk:\n%s" % (disko)))
                                    cmd = "umount /mnt/tmp"
                                    j.sal.process.execute(cmd, die=False)
                                    if os.path.ismount("/mnt/tmp"):
                                        raise j.exceptions.RuntimeError(
                                            "/mnt/tmp should not be mounted")

        return result

    def partitionsFind_Ext4Data(self):
        """
        looks for disks which are know to be data disks & are formatted ext4
        return [[$partpath,$gid,$partid,$size,$free]]
        """
        result = [item for item in self.partitionsFind(
            busy=False, ttype="ext4", ssd=False, prefix="sd", minsize=300, maxsize=5000)]
        return result

    def partitionsMount_Ext4Data(self):
        for path, partnr, size, free, ssd in self.partitionsFind_Ext4Data():
            mntdir = "/mnt/datadisks/%s" % partnr
            j.sal.fs.createDir(mntdir)
            cmd = "mount %s %s" % (path, mntdir)
            j.sal.process.execute(cmd)

    def partitionsUnmount_Ext4Data(self):
        partitions = self.partitionsGet_Ext4Data()
        for partid, size, free in partitions:
            mntdir = "/mnt/datadisks/%s" % partid
            cmd = "umount %s" % (mntdir)
            j.sal.process.execute(cmd)

    def partitionsGetMounted_Ext4Data(self):
        """
        find disks which are mounted
        @return [[$partid,$size,$free]]
        """
        # from IPython import embed
        # embed()
        # TODO
        pass
