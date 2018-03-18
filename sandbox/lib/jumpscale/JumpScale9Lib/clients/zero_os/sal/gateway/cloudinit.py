import time
from js9 import j




class CloudInit():
    def __init__(self, container, config):

        self.container = container
        self.config = config
        self.CONFIGPATH = "/etc/cloud-init"

    def apply_config(self):
        self.cleanup(self.config.keys())

        for key, value in self.config.items():
            fpath = "%s/%s" % (self.CONFIGPATH, key)
            self.container.upload_content(fpath, value)
        if not self.is_running():
            self.start()

    def cleanup(self, macaddresses):
        configs = self.container.client.filesystem.list(self.CONFIGPATH)
        for config in configs:
            if config["name"] not in macaddresses:
                self.container.client.filesystem.remove("%s/%s" % (self.CONFIGPATH, config["name"]))

    def start(self):
        if not self.is_running():
            self.container.client.system(
                'cloud-init-server \
                -bind 127.0.0.1:8080 \
                -config {config}'
                .format(config=self.CONFIGPATH),
                id='cloudinit.{}'.format(self.container.name))

        start = time.time()
        while time.time() < start + 10:
            if self.is_running():
                return
            time.sleep(0.5)
        raise RuntimeError('Failed to start cloudinit server')

    def is_running(self):
        for port in self.container.client.info.port():
            if port['network'] == 'tcp' and port['port'] == 8080 and port['ip'] == '127.0.0.1':
                return True
        return False
