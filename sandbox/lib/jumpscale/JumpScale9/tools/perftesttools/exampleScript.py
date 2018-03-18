from js9 import j

j.application.start("pertests")


def singleLocalNodeTest():
    settings = j.application.getAppInstanceHRD(name='vnas_setup', instance='main', domain='openvcloud')

    frontend_ip = settings.getStr('addr.frontend.master')

    j.tools.perftesttools.init(monitorNodeIp="localhost", sshPort=22, redispasswd="", testname="vnas")

    monitor = j.tools.perftesttools.getNodeMonitor()
    # host = j.tools.perftesttools.getNodeHost("192.168.103.248", 22, name="host1")

    nas = j.tools.perftesttools.getNodeNAS(frontend_ip, 22, fstype="xfs",
                                           role='vnas', name="nas1", debugdisk="/dev/sda")
    # nas.autoInitDisks(nbrdisk=2)
    nas.createLoopDev(size=500, backend_file='/storage/vnas/loop_device')
    nas.ready()  # call ready when all disks ready

    nas.perftester.sequentialReadWrite(size="2000m", nrfiles=1)


# def multiNodeMultDiskStripTest():

#     """
#     if you want to work from the monitoring vm: (remote option)
#     on monitoring vm do, to make sure there are keys & ssh-agent is loaded
#         js 'j.sal.ssh.sshagent_start(createkeys=True)'
#         #now logout & back login into that node, this only needs to happen once

#     """

#     nrdisks=6

#     j.tools.perftesttools.init(monitorNodeIp="192.168.103.252",sshPort=22,sshkey=mgmtkey)

#     monitor=j.tools.perftesttools.getNodeMonitor()

#     nasses=[]
#     nasipaddr=["192.168.103.240","192.168.103.239","192.168.103.238","192.168.103.237"]
#     #first init all nasses which takes some time
#     for ipaddr in nasipaddr:
#         nas=j.tools.perftesttools.getNodeNas(ipaddr,22,fstype="xfs")
#         nas.autoInitDisks(nbrdisk=6)
#         nasses.append(nas)
#         nas.startMonitor(cpu=0,disks=1,net=0)

#     #now start all the nas perftests
#     for i in range(len(nasipaddr)):
#         nas=nasses[i]
#         #will write 3 parallel file sequential on each disk
#         #each as has 6 disks, so 18 parallel writes
#         nas.perftester.sequentialWriteReadBigBlock(nrfilesParallel=3)

#     hosts=[]
#     hostsip=["10.10.10.1","10.10.10.2","10.10.10.3","10.10.10.4"]
#     for ipaddr in hostsip:
#         host=j.tools.perftesttools.getNodeHost(ipaddr,22)
#         hosts.append(host)
#         host.startMonitor(cpu=1,disks=0,net=0)


# multiNodeMultDiskStripTest()
singleLocalNodeTest()
