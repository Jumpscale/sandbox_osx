from JumpScale9Lib.sal.kvm.Network import Network
from JumpScale9Lib.sal.kvm.Interface import Interface
from JumpScale9Lib.sal.kvm.Disk import Disk
from JumpScale9Lib.sal.kvm.Pool import Pool
from JumpScale9Lib.sal.kvm.StorageController import StorageController
from JumpScale9Lib.sal.kvm.KVMController import KVMController
from JumpScale9Lib.sal.kvm.Machine import Machine
from JumpScale9Lib.sal.kvm.CloudMachine import CloudMachine
from JumpScale9Lib.sal.kvm.MachineSnapshot import MachineSnapshot

JSBASE = j.application.jsbase_get_class()
class KVM(JSBASE):

    def __init__(self):

        self.__jslocation__ = "j.sal.kvm"
        JSBASE.__init__(self)
        self.__imports__ = "libvirt-python"
        self.KVMController = KVMController
        self.Machine = Machine
        self.MachineSnapshot = MachineSnapshot
        self.Network = Network
        self.Interface = Interface
        self.Disk = Disk
        self.Pool = Pool
        self.StorageController = StorageController
        self.CloudMachine = CloudMachine
