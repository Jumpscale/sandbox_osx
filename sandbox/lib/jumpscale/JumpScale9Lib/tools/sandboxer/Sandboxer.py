from js9 import j

import re
import os

JSBASE = j.application.jsbase_get_class()

from .SandboxPython import SandboxPython
class Dep(JSBASE):

    def __init__(self, name, path):
        JSBASE.__init__(self)
        self.name = name
        self.path = path
        if j.sal.fs.isLink(self.path):
            link = j.sal.fs.readLink(self.path)
            if j.sal.fs.exists(path=link):
                self.path = link
                return
            else:
                base = j.sal.fs.getDirName(self.path)
                potpath = j.sal.fs.joinPaths(base, link)
                if j.sal.fs.exists(potpath):
                    self.path = potpath
                    return
        else:
            if j.sal.fs.exists(self.path):
                return
        raise j.exceptions.RuntimeError(
            "could not find lib (dep): '%s'" % self.path)

    def copyTo(self, path):
        dest = j.sal.fs.joinPaths(path, self.name)
        dest = dest.replace("//", "/")
        j.sal.fs.createDir(j.sal.fs.getDirName(dest))
        if dest != self.path:  # don't copy to myself
            # self.logger.debug("DEPCOPY: %s %s" % (self.path, dest))
            if not j.sal.fs.exists(dest):
                j.sal.fs.copyFile(self.path, dest)
            j.tools.sandboxer._done.append(dest)

    def __str__(self):
        return "%-40s %s" % (self.name, self.path)

    __repr__ = __str__

class Sandboxer(JSBASE):
    """
    sandbox any linux app
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.sandboxer"
        JSBASE.__init__(self)
        self._done = []
        self.exclude = ["libpthread.so", "libltdl.so", "libm.so", "libresolv.so",
                        "libz.so", "libgcc", "librt", "libstdc++", "libapt", "libdbus", "libselinux"]
        self.original_size = 0
        self.new_size = 0
        self.python = SandboxPython()

    def _ldd(self, path, result={}):

        if j.sal.fs.getFileExtension(path) in ["py", "pyc", "cfg", "hrd", "bak", "txt",
                                               "png", "gif", "css", "js", "wiki", "spec", "sh", "jar", "xml", "lua"]:
            return result

        if path not in self._done:
            self.logger.debug(("check:%s" % path))

            cmd = "ldd %s" % path
            rc, out, err = j.sal.process.execute(cmd, die=False)
            if rc > 0:
                if out.find("not a dynamic executable") != -1:
                    return result
            for line in out.split("\n"):
                line = line.strip()
                if line == "":
                    continue
                if line.find('=>') == -1:
                    continue

                name, lpath = line.split("=>")
                name = name.strip().strip("\t")
                name = name.replace("\\t", "")
                lpath = lpath.split("(")[0]
                lpath = lpath.strip()
                if lpath == "":
                    continue
                if name.find("libc.so") != 0 and name.lower().find("libx") != 0 and name not in self._done \
                        and name.find("libdl.so") != 0:
                    excl = False
                    for toexeclude in self.exclude:
                        if name.lower().find(toexeclude.lower()) != -1:
                            excl = True
                    if not excl:
                        self.logger.debug(("found:%s" % name))
                        try:
                            result[name] = Dep(name, lpath)
                            self._done.append(name)
                            result = self._ldd(lpath, result)
                        except Exception as e:
                            self.logger.debug(e)

        self._done.append(path)
        return result

    def findLibs(self, path):
        """
        not needed to use manually, is basically ldd
        """
        result = self._ldd(path)
        return result

    def sandboxLibs(self, path, dest=None, recursive=False):
        """
        find binaries on path and look for supporting libs, copy the libs to dest
        default dest = '%s/bin/'%j.dirs.JSBASEDIR
        """
        if dest is None:
            dest = "%s/bin/" % j.dirs.BASEDIR
        if j.sal.fs.isDir(path):
            # do all files in dir
            for item in j.sal.fs.listFilesInDir(path, recursive=False, followSymlinks=True, listSymlinks=False):
                if j.sal.fs.isExecutable(item) or j.sal.fs.getFileExtension(item) == "so":
                    self.sandboxLibs(item, dest, recursive=False)
            if recursive:
                for item in j.sal.fs.listDirsInDir(path, recursive=False):
                    self.sandboxLibs(item, dest, recursive)

        else:
            result = self.findLibs(path)
            for name, deb in list(result.items()):
                deb.copyTo(dest)

    def copyTo(self, path, dest, excludeFileRegex=[], excludeDirRegex=[], excludeFiltersExt=["pyc", "bak"]):

        self.logger.debug("SANDBOX COPY: %s to %s" % (path, dest))

        excludeFileRegex = [re.compile(r'%s' % item)
                            for item in excludeFileRegex]
        excludeDirRegex = [re.compile(r'%s' % item)
                           for item in excludeDirRegex]
        for extregex in excludeFiltersExt:
            excludeFileRegex.append(re.compile(r'(\.%s)$' % extregex))

        def callbackForMatchDir(path, arg):
            # self.logger.debug ("P:%s"%path)
            for item in excludeDirRegex:
                if(len(re.findall(item, path)) > 0):
                    return False
            return True

        def callbackForMatchFile(path, arg):
            # self.logger.debug ("F:%s"%path)
            for item in excludeFileRegex:
                if(len(re.findall(item, path)) > 0):
                    return False
            return True

        def callbackFile(src, args):
            path, dest = args
            subpath = j.sal.fs.pathRemoveDirPart(src, path)
            if subpath.startswith("dist-packages"):
                subpath = subpath.replace("dist-packages/", "")
            if subpath.startswith("site-packages"):
                subpath = subpath.replace("site-packages/", "")

            dest2 = dest + "/" + subpath
            j.sal.fs.createDir(j.sal.fs.getDirName(dest2))
            # self.logger.debug ("C:%s"%dest2)
            j.sal.fs.copyFile(src, dest2, overwriteFile=True)

        j.sal.fswalker.walkFunctional(path, callbackFunctionFile=callbackFile, callbackFunctionDir=None, arg=(
            path, dest), callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=callbackForMatchFile)



    # def dedupe(self, path, storpath, name, excludeFiltersExt=[
    #            "pyc", "bak"], append=False, reset=False, removePrefix="", compress=True, delete=False, excludeDirs=[]):
    #     def copy2dest(src, removePrefix):
    #         if j.sal.fs.isLink(src):
    #             srcReal = j.sal.fs.readLink(src)
    #             if not j.sal.fs.isAbsolute(srcReal):
    #                 srcReal = j.sal.fs.joinPaths(j.sal.fs.getParent(src), srcReal)
    #         else:
    #             srcReal = src

    #         md5 = j.data.hash.md5(srcReal)
    #         dest2 = "%s/%s/%s/%s" % (storpath2, md5[0], md5[1], md5)
    #         dest2_bro = "%s/%s/%s/%s.bro" % (storpath2, md5[0], md5[1], md5)
    #         path_src = j.tools.path.get(srcReal)
    #         self.original_size += path_src.size
    #         if compress:
    #             self.logger.debug("- %-100s %sMB" % (srcReal, round(path_src.size / 1000000, 1)))
    #             if delete or not j.sal.fs.exists(dest2_bro):
    #                 cmd = "bro --quality 7 --input '%s' --output %s" % (srcReal, dest2_bro)
    #                 # self.logger.debug (cmd)
    #                 j.sal.process.execute(cmd)
    #                 if not j.sal.fs.exists(dest2_bro):
    #                     raise j.exceptions.RuntimeError("Could not do:%s" % cmd)
    #                 path_dest = j.tools.path.get(dest2_bro)
    #                 size = path_dest.size
    #                 self.new_size += size
    #                 if not self.original_size == 0:
    #                     efficiency = round(self.new_size / self.original_size, 3)
    #                 else:
    #                     efficiency = 1
    #                 if not path_src.size == 0:
    #                     efficiency_now = round(path_dest.size / path_src.size, 3)
    #                 else:
    #                     efficiency_now = 0
    #                 self.logger.debug("- %-100s %-6s %-6s %sMB" %
    #                       ("", efficiency, efficiency_now, round(self.original_size / 1000000, 1)))
    #         else:
    #             j.sal.fs.copyFile(srcReal, dest2)

    #         stat = j.sal.fs.statPath(srcReal)

    #         if removePrefix != "":
    #             if src.startswith(removePrefix):
    #                 src = src[len(removePrefix):]
    #                 if src[0] != "/":
    #                     src = "/" + src

    #         out = "%s|%s|%s\n" % (src, md5, stat.st_size)
    #         return out

    #     if reset:
    #         j.sal.fs.removeDirTree(storpath)

    #     storpath2 = j.sal.fs.joinPaths(storpath, "files")
    #     j.sal.fs.createDir(storpath2)
    #     j.sal.fs.createDir(j.sal.fs.joinPaths(storpath, "md"))
    #     for i1 in "1234567890abcdef":
    #         for i2 in "1234567890abcdef":
    #             j.sal.fs.createDir("%s/%s/%s" % (storpath2, i1, i2))

    #     self.logger.debug("DEDUPE: %s to %s" % (path, storpath))

    #     plistfile = j.sal.fs.joinPaths(storpath, "md", "%s.flist" % name)

    #     if append and j.sal.fs.exists(path=plistfile):
    #         out = j.sal.fs.fileGetContents(plistfile)
    #     else:
    #         j.sal.fs.remove(plistfile)
    #         out = ""

    #     # excludeFileRegex=[]
    #     # for extregex in excludeFiltersExt:
    #     #     excludeFileRegex.append(re.compile(ur'(\.%s)$'%extregex))
    #     def skipDir(src):
    #         for d in excludeDirs:
    #             if src.startswith(d):
    #                 return True
    #         return False

    #     if not j.sal.fs.isDir(path):
    #         out += copy2dest(path, removePrefix)
    #     else:
    #         for src in j.sal.fs.listFilesInDir(path, recursive=True, exclude=[
    #                                            "*.pyc", "*.git*"], followSymlinks=True, listSymlinks=True):
    #             if skipDir(src):
    #                 continue
    #             out += copy2dest(src, removePrefix)

    #     out = j.data.text.sort(out)
    #     j.sal.fs.writeFile(plistfile, out)

