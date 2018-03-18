import shlex
import json

from .Response import JSONResponse
from .FilesystemManager import FilesystemManager
from .IPManager import IPManager
from .JobManager import JobManager
from .ProcessManager import ProcessManager
from .InfoManager import InfoManager
from .Response import ResultError
from . import typchk
from  js9 import j

DefaultTimeout = 10  # seconds



class BaseClient():
    _system_chk = typchk.Checker({
        'name': str,
        'args': [str],
        'dir': str,
        'stdin': str,
        'env': typchk.Or(typchk.Map(str, str), typchk.IsNone()),
    })

    _bash_chk = typchk.Checker({
        'stdin': str,
        'script': str,
    })

    def __init__(self, timeout=None):

        if timeout is None:
            self.timeout = DefaultTimeout
        else:
            self.timeout = timeout
        self._info = InfoManager(self)
        self._job = JobManager(self)
        self._process = ProcessManager(self)
        self._filesystem = FilesystemManager(self)
        self._ip = IPManager(self)

    @property
    def info(self):
        """
        info manager
        :return:
        """
        return self._info

    @property
    def job(self):
        """
        job manager
        :return:
        """
        return self._job

    @property
    def process(self):
        """
        process manager
        :return:
        """
        return self._process

    @property
    def filesystem(self):
        """
        filesystem manager
        :return:
        """
        return self._filesystem

    @property
    def ip(self):
        """
        ip manager
        :return:
        """
        return self._ip

    def raw(self, command, arguments, queue=None, max_time=None, stream=False, tags=None, id=None):
        """
        Implements the low level command call, this needs to build the command structure
        and push it on the correct queue.

        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param queue: command queue (commands on the same queue are executed sequentially)
        :param max_time: kill job server side if it exceeded this amount of seconds
        :param stream: If True, process stdout and stderr are pushed to a special queue (stream:<id>) so
            client can stream output
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :return: Response object
        """
        raise NotImplemented()

    def sync(self, command, arguments, tags=None, id=None):
        """
        Same as self.raw except it do a response.get() waiting for the command execution to finish and reads the result
        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :return: Result object
        """
        response = self.raw(command, arguments, tags=tags, id=id)

        result = response.get()
        if result.state != 'SUCCESS':
            if not result.code:
                result.code = 500
            raise ResultError(msg='%s' % result.data, code=result.code)


        return result

    def json(self, command, arguments, tags=None, id=None):
        """
        Same as self.sync except it assumes the returned result is json, and loads the payload of the return object
        if the returned (data) is not of level (20) an error is raised.
        :Return: Data
        """
        result = self.sync(command, arguments, tags=tags, id=id)
        if result.level != 20:
            raise RuntimeError('invalid result level, expecting json(20) got (%d)' % result.level)

        return json.loads(result.data)

    def ping(self):
        """
        Ping a node, checking for it's availability. a Ping should never fail unless the node is not reachable
        or not responsive.
        :return:
        """
        return self.json('core.ping', {})

    def system(self, command, dir='', stdin='', env=None, queue=None, max_time=None, stream=False, tags=None, id=None):
        """
        Execute a command

        :param command:  command to execute (with its arguments) ex: `ls -l /root`
        :param dir: CWD of command
        :param stdin: Stdin data to feed to the command stdin
        :param env: dict with ENV variables that will be exported to the command
        :param id: job id. Auto generated if not defined.
        :return:
        """
        parts = shlex.split(command)
        if len(parts) == 0:
            raise ValueError('invalid command')

        args = {
            'name': parts[0],
            'args': parts[1:],
            'dir': dir,
            'stdin': stdin,
            'env': env,
        }

        self._system_chk.check(args)
        response = self.raw(command='core.system', arguments=args,
                            queue=queue, max_time=max_time, stream=stream, tags=tags, id=id)

        return response

    def bash(self, script, stdin='', queue=None, max_time=None, stream=False, tags=None, id=None):
        """
        Execute a bash script, or run a process inside a bash shell.

        :param script: Script to execute (can be multiline script)
        :param stdin: Stdin data to feed to the script
        :param id: job id. Auto generated if not defined.
        :return:
        """
        args = {
            'script': script,
            'stdin': stdin,
        }
        self._bash_chk.check(args)
        response = self.raw(command='bash', arguments=args,
                            queue=queue, max_time=max_time, stream=stream, tags=tags, id=id)

        return response

    def subscribe(self, job, id=None):
        """
        Subscribes to job logs. It return the subscribe Response object which you will need to call .stream() on
        to read the output stream of this job.

        Calling subscribe multiple times will cause different subscriptions on the same job, each subscription will
        have a copy of this job streams.

        Note: killing the subscription job will not affect this job, it will also not cause unsubscripe from this stream
        the subscriptions will die automatically once this job exits.

        example:
            job = client.system('long running job')
            subscription = client.subscribe(job.id)

            subscription.stream() # this will print directly on stdout/stderr check stream docs for more details.

        hint: u can give an optional id to the subscriber (otherwise a guid will be generate for you). You probably want
        to use this in case your job watcher died, so u can hook on the stream of the current subscriber instead of creating a new one

        example:
            job = client.system('long running job')
            subscription = client.subscribe(job.id, 'my-job-subscriber')

            subscription.stream()

            # process dies for any reason
            # on next start u can simply do

            subscription = client.response_for('my-job-subscriber')
            subscription.stream()


        :param job: the job ID to subscribe to
        :param id: the subscriber ID (optional)
        :return: the subscribe Job object
        """
        return self.raw('core.subscribe', {'id': job}, stream=True, id=id)


class ContainerClient(BaseClient):
    class ContainerZerotierManager:
        def __init__(self, client, container):
            self._container = container
            self._client = client

        def info(self):
            return self._client.json('corex.zerotier.info', {'container': self._container})

        def list(self):
            return self._client.json('corex.zerotier.list', {'container': self._container})

    _raw_chk = typchk.Checker({
        'container': int,
        'command': {
            'command': str,
            'arguments': typchk.Any(),
            'queue': typchk.Or(str, typchk.IsNone()),
            'max_time': typchk.Or(int, typchk.IsNone()),
            'stream': bool,
            'tags': typchk.Or([str], typchk.IsNone()),
            'id': typchk.Or(str, typchk.IsNone()),

        }
    })

    def __init__(self, client, container):
        super().__init__(client.timeout)

        self._client = client
        self._container = container
        self._zerotier = ContainerClient.ContainerZerotierManager(client, container)  # not (self) we use core0 client

    @property
    def container(self):
        """
        :return: container id
        """
        return self._container

    @property
    def zerotier(self):
        """
        information about zerotier id
        :return:
        """
        return self._zerotier

    def raw(self, command, arguments, queue=None, max_time=None, stream=False, tags=None, id=None):
        """
        Implements the low level command call, this needs to build the command structure
        and push it on the correct queue.

        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param queue: command queue (commands on the same queue are executed sequentially)
        :param max_time: kill job server side if it exceeded this amount of seconds
        :param stream: If True, process stdout and stderr are pushed to a special queue (stream:<id>) so
            client can stream output
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :return: Response object
        """
        args = {
            'container': self._container,
            'command': {
                'command': command,
                'arguments': arguments,
                'queue': queue,
                'max_time': max_time,
                'stream': stream,
                'tags': tags,
                'id': id,
            },
        }

        # check input
        self._raw_chk.check(args)

        response = self._client.raw('corex.dispatch', args)

        result = response.get()
        if result.state != 'SUCCESS':
            raise RuntimeError('failed to dispatch command to container: %s' % result.data)

        cmd_id = json.loads(result.data)
        return self._client.response_for(cmd_id)

class ContainerManager():
    _nic = {
        'type': typchk.Enum('default', 'bridge', 'zerotier', 'vlan', 'vxlan'),
        'id': typchk.Or(str, typchk.Missing()),
        'name': typchk.Or(str, typchk.Missing()),
        'hwaddr': typchk.Or(str, typchk.Missing()),
        'config': typchk.Or(
            typchk.Missing(),
            {
                'dhcp': typchk.Or(bool, typchk.Missing()),
                'cidr': typchk.Or(str, typchk.Missing()),
                'gateway': typchk.Or(str, typchk.Missing()),
                'dns': typchk.Or([str], typchk.Missing()),
            }
        ),
        'monitor': typchk.Or(bool, typchk.Missing()),
    }

    _create_chk = typchk.Checker({
        'root': str,
        'mount': typchk.Or(
            typchk.Map(str, str),
            typchk.IsNone()
        ),
        'host_network': bool,
        'nics': [_nic],
        'port': typchk.Or(
            typchk.Map(int, int),
            typchk.IsNone()
        ),
        'privileged': bool,
        'hostname': typchk.Or(
            str,
            typchk.IsNone()
        ),
        'storage': typchk.Or(str, typchk.IsNone()),
        'name': typchk.Or(str, typchk.IsNone()),
        'identity': typchk.Or(str, typchk.IsNone()),
        'env': typchk.Or(typchk.IsNone(), typchk.Map(str, str))
    })

    _client_chk = typchk.Checker(
        typchk.Or(int, str)
    )

    _nic_add = typchk.Checker({
        'container': int,
        'nic': _nic,
    })

    _nic_remove = typchk.Checker({
        'container': int,
        'index': int,
    })

    DefaultNetworking = object()



    def __init__(self, client):
        self._client = client


    def create(self, root_url, mount=None, host_network=False, nics=DefaultNetworking, port=None, hostname=None, privileged=False, storage=None, name=None, tags=None, identity=None, env=None):
        """
        Creater a new container with the given root flist, mount points and
        zerotier id, and connected to the given bridges
        :param root_url: The root filesystem flist
        :param mount: a dict with {host_source: container_target} mount points.
                      where host_source directory must exists.
                      host_source can be a url to a flist to mount.
        :param host_network: Specify if the container should share the same network stack as the host.
                             if True, container creation ignores both zerotier, bridge and ports arguments below. Not
                             giving errors if provided.
        :param nics: Configure the attached nics to the container
                     each nic object is a dict of the format
                     {
                        'type': nic_type # default, bridge, zerotier, vlan, or vxlan (note, vlan and vxlan only supported by ovs)
                        'id': id # depends on the type, bridge name, zerotier network id, the vlan tag or the vxlan id
                        'name': name of the nic inside the container (ignored in zerotier type)
                        'hwaddr': Mac address of nic.
                        'config': { # config is only honored for bridge, vlan, and vxlan types
                            'dhcp': bool,
                            'cidr': static_ip # ip/mask
                            'gateway': gateway
                            'dns': [dns]
                        }
                     }
        :param port: A dict of host_port: container_port pairs (only if default networking is enabled)
                       Example:
                        `port={8080: 80, 7000:7000}`
        :param hostname: Specific hostname you want to give to the container.
                         if None it will automatically be set to core-x,
                         x beeing the ID of the container
        :param privileged: If true, container runs in privileged mode.
        :param storage: A Url to the ardb storage to use to mount the root flist (or any other mount that requires g8fs)
                        if not provided, the default one from core0 configuration will be used.
        :param name: Optional name for the container
        :param identity: Container Zerotier identity, Only used if at least one of the nics is of type zerotier
        :param env: a dict with the environment variables needed to be set for the container
        """

        if nics == self.DefaultNetworking:
            nics = [{'type': 'default'}]
        elif nics is None:
            nics = []

        args = {
            'root': root_url,
            'mount': mount,
            'host_network': host_network,
            'nics': nics,
            'port': port,
            'hostname': hostname,
            'privileged': privileged,
            'storage': storage,
            'name': name,
            'identity': identity,
            'env': env
        }

        # validate input
        self._create_chk.check(args)

        response = self._client.raw('corex.create', args, tags=tags)

        return JSONResponse(response)

    def list(self):
        """
        List running containers
        :return: a dict with {container_id: <container info object>}
        """
        return self._client.json('corex.list', {})

    def find(self, *tags):
        """
        Find containers that matches set of tags
        :param tags:
        :return:
        """
        tags = list(map(str, tags))
        return self._client.json('corex.find', {'tags': tags})

    def terminate(self, container):
        """
        Terminate a container given it's id

        :param container: container id
        :return:
        """
        self._client_chk.check(container)
        args = {
            'container': int(container),
        }
        response = self._client.raw('corex.terminate', args)

        result = response.get()
        if result.state != 'SUCCESS':
            raise RuntimeError('failed to terminate container: %s' % result.data)

    def nic_add(self, container, nic):
        """
        Hot plug a nic into a container

        :param container: container ID
        :param nic: {
                        'type': nic_type # default, bridge, zerotier, vlan, or vxlan (note, vlan and vxlan only supported by ovs)
                        'id': id # depends on the type, bridge name, zerotier network id, the vlan tag or the vxlan id
                        'name': name of the nic inside the container (ignored in zerotier type)
                        'hwaddr': Mac address of nic.
                        'config': { # config is only honored for bridge, vlan, and vxlan types
                            'dhcp': bool,
                            'cidr': static_ip # ip/mask
                            'gateway': gateway
                            'dns': [dns]
                        }
                     }
        :return:
        """
        args = {
            'container': container,
            'nic': nic
        }
        self._nic_add.check(args)

        return self._client.json('corex.nic-add', args)

    def nic_remove(self, container, index):
        """
        Hot unplug of nic from a container

        Note: removing a nic, doesn't remove the nic from the container info object, instead it sets it's state
        to `destroyed`.

        :param container: container ID
        :param index: index of the nic as returned in the container object info (as shown by container.list())
        :return:
        """
        args = {
            'container': container,
            'index': index
        }
        self._nic_remove.check(args)

        return self._client.json('corex.nic-remove', args)

    def client(self, container):
        """
        Return a client instance that is bound to that container.

        :param container: container id
        :return: Client object bound to the specified container id
        Return a ContainerResponse from container.create
        """

        self._client_chk.check(container)
        return ContainerClient(self._client, int(container))

    def backup(self, container, url):
        """
        Backup a container to the given restic url
        all restic urls are supported

        :param container:
        :param url: Url to restic repo
                examples
                (file:///path/to/restic/?password=<password>)

        :return: Json response to the backup job (do .get() to get the snapshot ID
        """

        args = {
            'container': container,
            'url': url,
        }

        return JSONResponse(self._client.raw('corex.backup', args))

    def restore(self, url, tags=None):
        """
        Full restore of a container backup. This restore method will recreate
        an exact copy of the backedup container (including same network setup, and other
        configurations as defined by the `create` method.

        To just restore the container data, and use new configuration, use the create method instead
        with the `root_url` set to `restic:<url>`

        :param url: Snapshot url, the snapshot ID is passed as a url fragment
                    examples:
                        `file:///path/to/restic/repo?password=<password>#<snapshot-id>`
        :param tags: this will always override the original container tags (even if not set)
        :return:
        """
        args = {
            'url': url,
        }

        return JSONResponse(self._client.raw('corex.restore', args, tags=tags))

