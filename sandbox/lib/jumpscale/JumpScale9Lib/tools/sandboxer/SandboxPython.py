from js9 import j

JSBASE = j.application.jsbase_get_class()



class SandboxPython(JSBASE):
    """
    sandbox python
    """

    def __init__(self):
        JSBASE.__init__(self)
        if j.core.platformtype.myplatform.isMac:
            self.JS9FILE = "/usr/local/lib/python3.6/site-packages/js9.py"
        else:
            self.JS9FILE = "/usr/lib/python3/dist-packages/js9.py"

    @property
    def BUILDDIR(self):
        return  j.tools.prefab.local.runtimes.python.BUILDDIRL
        
    @property
    def CODEDIR(self):
        return  j.tools.prefab.local.runtimes.python.CODEDIRL

    @property
    def PACKAGEDIR(self):
        return  j.dirs.BUILDDIR + "/sandbox/python3/"

    def build(self):
        """
        builds python and returns the build dir
        """
        path = j.tools.prefab.local.runtimes.python.build()
        return path

    def do(self, path="", dest="", build=True):
        """
        js9 'j.tools.sandboxer.python.do()'

        if dest == "" will be j.dirs.BUILDDIR+"/sandbox/python3/"

        """

        j.tools.prefab.local.system.package.install("zip")

        if build:
            path = self.build()

        if path == "":
            path =  self.BUILDDIRL

        if not j.sal.fs.exists("%s/bin/python3.6" % path):
            raise RuntimeError(
                "am not in compiled python dir, need to find %s/bin/python3.6" % path)

        if dest == "":
            dest = self.PACKAGEDIR

        j.sal.fs.remove(dest)
        j.sal.fs.createDir(dest)

        for item in ["bin", "include", "lib"]:
            j.sal.fs.createDir("%s/%s" % (dest, item))

        for item in ["pip3","python3.6","ipython"]:
            src0 = "%s/bin/%s"%(path,item)
            dest0 = "%s/bin/%s"%(dest,item)
            j.sal.fs.copyFile(src0,dest0)

        def dircheck(name):
            for item in ["lib2to3","idle",".dist-info","__pycache__","site-packages"]:
                if name.find(item) is not -1:
                    return False
            return True

        def binarycheck(path):
            if "parso" in path:
                return True
            files = j.sal.fs.listFilesInDir(path, recursive=True, filter="*.so", followSymlinks=True)
            if len(files)>0:
                self.logger.debug("found binary files in:%s"%path)
                return True
            return False

        #ignore files which are not relevant, 

        ignoredir=['.egg-info', '.dist-info',"__pycache__","audio","tkinter","audio","test"]
        ignorefiles=['.egg-info',".pyc"]

        src = "%s/lib/python3.6/site-packages"%(path)
        for ddir in  j.sal.fs.listDirsInDir(src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True):
            if dircheck(ddir):
                src0= src+"/%s"%ddir
                if binarycheck(src0):
                    dest0 = "%s/lib/pythonbin/%s"%(dest,ddir)
                else:
                    dest0 = "%s/lib/python/%s"%(dest,ddir)      
                self.logger.debug("copy lib:%s ->%s"%(src0,dest0))
                j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)

        src = "%s/lib/python3.6"%(path)
        for ddir in  j.sal.fs.listDirsInDir(src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True):
            if dircheck(ddir):
                src0= src+"/%s"%ddir
                if binarycheck(src0):
                    dest0 = "%s/lib/pythonbin/%s"%(dest,ddir)
                else:
                    dest0 = "%s/lib/python/%s"%(dest,ddir)      
                self.logger.debug("copy lib:%s ->%s"%(src0,dest0))
                self.logger.debug("copy %s %s"%(src0,dest0))
                j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)

        for item in  j.sal.fs.listFilesInDir(src, recursive=False, filter="*.py", exclude=ignorefiles, followSymlinks=True):
            fname = j.sal.fs.getBaseName(item)
            dest0  = "%s/lib/python/%s"%(dest,fname) 
            self.logger.debug("copy %s %s"%(item,dest0))
            j.sal.fs.copyFile(item,dest0)


        for item in  j.sal.fs.listFilesInDir( "%s/lib/python3.6/site-packages"%(path), recursive=False,exclude=ignorefiles, followSymlinks=True):
            
            fname = j.sal.fs.getBaseName(item)
            if fname.endswith(".so"):
                dest0  = "%s/lib/pythonbin/%s"%(dest,fname) 
            else:
                dest0  = "%s/lib/python/%s"%(dest,fname) 
            self.logger.debug("copy %s %s"%(item,dest0))
            j.sal.fs.copyFile(item,dest0)

        remove=["codecs_jp","codecs_hk","codecs_cn","codecs_kr","testcapi","tkinter","audio"]

        #remove some stuff we don't need
        for item in  j.sal.fs.listFilesInDir("%s/lib"%(dest), recursive=True):
            if item.endswith(".c") or item.endswith(".h"):
                j.sal.fs.remove(item)
                pass
            for x in remove:
                if item.find(x) is not -1:
                    j.sal.fs.remove(item)
                    pass

        j.tools.sandboxer.python.jumpscale_add()

        self._zip(dest=dest)
        self.env_write(dest=dest)

    def _zip(self,dest=""):
        if dest == "":
            dest = j.dirs.BUILDDIR + "/sandbox/python3/"                
        cmd = "cd %s/lib/python;zip -r ../python.zip *;cd %s/lib;rm -rf python"%(dest,dest)
        j.sal.process.execute(cmd)
        cmd = "cd %s;rm -f ../js9_sandbox.zip;zip -r ../js9_sandbox.zip *"%(dest)
        j.sal.process.execute(cmd)

    def jumpscale_add(self,dest=""):
        """
        js9 'j.tools.sandboxer.python.jumpscale_add()'
        """        

        def process(c):
            out = ""
            for line in c.split("\n"):
                if line.startswith("#!"):
                    out += "#! /usr/bin/env python3.6\n" 
                    continue
                out+="%s\n"%line
            return out
                    

        if dest == "":
            dest = self.PACKAGEDIR

        ignoredir=['.egg-info', '.dist-info',"__pycache__","audio","tkinter","audio","test"]
        ignorefiles=['.egg-info',".pyc"]            

        for key,p in  j.core.state.config_js["plugins"].items():
            dest0 = "%s/lib/jumpscale/%s"%(dest,key)
            j.sal.fs.copyDirTree(p, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)

            if key == "JumpScale9":
                jscodedir="/".join(p.rstrip("/").split("/")[:-1])
                for item in j.sal.fs.listFilesInDir("%s/cmds"%jscodedir):
                    fname = j.sal.fs.getBaseName(item)
                    dest0 = "%s/bin/%s"%(dest,fname)
                    C= j.sal.fs.readFile(item)
                    C=process(C)
                    j.sal.fs.writeFile(dest0,C)
                    j.sal.fs.chmod(dest0, 0o770)
                    
                            
        j.sal.fs.touch("%s/lib/jumpscale/__init__.py"%(dest))

        j.sal.fs.copyFile(self.JS9FILE,"%s/lib/jumpscale/js9.py"%(dest))

        self.env_write(dest)

        

    def env_write(self,dest=""):        
        """
        js9 'j.tools.sandboxer.python.env_write()'
        """

        if dest == "":
            dest = self.PACKAGEDIR    

        C="""
        export PBASE=`pwd`

        export PATH=$PBASE/bin:/bin:/usr/local/bin:/usr/bin
        export PYTHONPATH=$PBASE/lib/python:$PBASE/lib/pythonbin:$PBASE/lib/python.zip:$PBASE/lib/jumpscale:$PBASE/lib/pythonbin/lib-dynload:$PBASE/bin
        export PYTHONHOME=$PBASE

        export LIBRARY_PATH="$PBASE/bin:$PBASE/lib"
        export LD_LIBRARY_PATH="$LIBRARY_PATH"

        export LDFLAGS="-L$LIBRARY_PATH/"

        export LC_ALL=en_US.UTF-8
        export LANG=en_US.UTF-8

        export PS1="JS9: "        

        """
        j.sal.fs.writeFile("%s/env.sh" %  dest, j.data.text.strip(C))

        print("to test:\ncd %s;source env.sh"%dest)

