import signal
import time

from zeroos.orchestrator.sal import templates
from js9 import j




class HTTPServer():
    def __init__(self, container, service, httpproxies):

        self.container = container
        self.service = service
        self.httpproxies = httpproxies

    def id(self):
        return 'http.{}'.format(self.service.name)

    def apply_rules(self):
        # caddy
        type = self.service.model.data.type
        caddyconfig = templates.render('caddy.conf', type=type, httpproxies=self.httpproxies).strip()
        conf = '/etc/caddy-{}.conf'.format(type)
        self.container.upload_content(conf, caddyconfig)
        self.container.client.job.kill(self.id(), int(signal.SIGUSR1))
        if caddyconfig == '':
            return
        self.container.client.system(
            'caddy -agree -conf {}'.format(conf), stdin='\n', id=self.id())
        start = time.time()
        while start + 10 > time.time():
            if self.is_running():
                return True
            time.sleep(0.5)
        raise RuntimeError("Failed to start caddy server")

    def is_running(self):
        try:
            self.container.client.job.list(self.id())
        except:
            return False
        portnr = 80 if self.service.model.data.type == 'http' else 443
        for port in self.container.client.info.port():
            if port['network'] .startswith('tcp') and port['port'] == portnr:
                return True
        return False
