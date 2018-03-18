import io

from js9 import j
from pssh.ssh2_client import SSHClient as PSSHClient

from .SSHClientBase import SSHClientBase


class SSHClient(SSHClientBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        SSHClientBase.__init__(self, instance=instance,
                               data=data, parent=parent, interactive=interactive)
        self._logger = j.logger.get("ssh client: %s:%s(%s)" % (self.addr_variable, self.port, self.login))
        self._client = None
        self._prefab = None

    @property
    def client(self):
        if self.sshkey:
            self.sshkey.load()
        passwd = self.passwd
        self._client = PSSHClient(self.addr_variable,
                                  user=self.login,
                                  password=passwd,
                                  port=self.port,
                                  num_retries=self.timeout / 6,
                                  retry_delay=1,
                                  allow_agent=self.allow_agent,
                                  timeout=5)

        return self._client

    def execute(self, cmd, showout=True, die=True):
        channel, _, stdout, stderr, _ = self.client.run_command(cmd)
        self._client.wait_finished(channel)

        def _consume_stream(stream, printer):
            buffer = io.StringIO()
            for line in stream:
                buffer.write(line + '\n')
                if showout:
                    printer(line)
            return buffer

        out = _consume_stream(stdout, self.logger.info)
        err = _consume_stream(stderr, self.logger.error)

        rc = channel.get_exit_status()
        output = out.getvalue()
        out.close()
        error = err.getvalue()
        err.close()
        channel.close()

        if rc and die:
            raise j.exceptions.RuntimeError("Cannot execute (ssh):\n%s\noutput:\n%serrors:\n%s" % (cmd, output, error))

        return rc, output, error

    def connect(self):
        self.client

    # def connectViaProxy(self, host, username, port, identityfile, proxycommand=None):
    #     # TODO: Fix this
    #     self.usesproxy = True
    #     client = paramiko.SSHClient()
    #     client._policy = paramiko.WarningPolicy()
    #     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     import os.path
    #     self.host = host
    #     cfg = {'hostname': host, 'username': username, "port": port}
    #     self.addr = host
    #     self.user = username

    #     if identityfile is not None:
    #         cfg['key_filename'] = identityfile
    #         self.key_filename = cfg['key_filename']

    #     if proxycommand is not None:
    #         cfg['sock'] = paramiko.ProxyCommand(proxycommand)
    #     cfg['timeout'] = 5
    #     cfg['allow_agent'] = True
    #     cfg['banner_timeout'] = 5
    #     self.cfg = cfg
    #     self.forward_agent = True
    #     self._client = client
    #     self._client.connect(**cfg)

    #     return self._client

    def reset(self):
        with self._lock:
            if self._client is not None:
                self._client = None

    @property
    def sftp(self):
        return self.client._make_sftp()

    def close(self):
        # TODO: make sure we don't need to clean anything
        pass

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("dest path should be absolute")

        dest = "%s@%s:%s" % (self.config.data['login'], self.addr_variable, dest)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=True,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                ".egg-info",
                ".dist-info",
                "__pycache__"],
            ignorefiles=[".egg-info"],
            rsync=True,
            ssh=True,
            sshport=self.port_variable,
            recursive=recursive)

    def rsync_down(self, source, dest, source_prefix="", recursive=True):
        if source[0] != "/":
            raise j.exceptions.RuntimeError("source path should be absolute")
        source = "%s@%s:%s" % (self.config.data['login'], self.addr_variable, source)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=True,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                ".egg-info",
                ".dist-info"],
            ignorefiles=[".egg-info"],
            rsync=True,
            ssh=True,
            sshport=self.port_variable,
            recursive=recursive)

    @property
    def prefab(self):
        if self._prefab:
            return self._prefab
        ex = j.tools.executor
        executor = ex.getSSHViaProxy(self.addr_variable) if self.config.data['proxy'] else ex.ssh_get(self) 
        if self.config.data["login"] != "root":
            executor.state_disabled = True
        self._prefab = executor.prefab
        return self._prefab

    def ssh_authorize(self, user, key):
        sshkey = j.clients.sshkey.get(key)
        pubkey = sshkey.pubkey
        self.prefab.system.ssh.authorize(user=user, key=pubkey)
