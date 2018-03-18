

from base import BaseService, BaseServiceSection
from js9 import j
JSBASE = j.application.jsbase_get_class()


class PureFTPError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class PureFTP(BaseService, BaseServiceSection, JSBASE):
    PACKAGE = 'pure-ftpd'
    SECTION = 'pure-ftpd'

    EXPOSED_FIELDS = [
        'port',
        'authentication',
        'logpid',
        'fscharset',
        'clientcharset',
        'trustedgid',
        'maxclientsnumber',
        'maxclientsperip',
        'syslogfacility',
        'fortunesfile',
        'pidfile',
        'maxidletime',
        'maxdiskusagepct',
        'login',
        'limitrecursion',
        'maxload',
        'natmode',
        'uploadscript',
        'altlog',
        'passiveportrange',
        'forcepassiveip',
        'anonymousratio',
        'userratio',
        'autorename',
        'antiwarez',
        'bind',
        'anonymousbandwidth',
        'userbandwidth',
        'minuid',
        'umask',
        'bonjour',
        'trustedip',
        'peruserlimits',
        'customerproof'
    ]

    EXPOSED_BOOLEAN_FIELDS = [
        'enabled',
        'notruncate',
        'ipv4only',
        'ipv6only',
        'chrooteveryone',
        'brokenclientscompatibility',
        'daemonize',
        'verboselog',
        'displaydotfiles',
        'anonymousonly',
        'noanonymous',
        'norename',
        'dontresolve',
        'anonymouscantupload',
        'createhomedir',
        'keepallfiles',
        'anonymouscancreatedirs',
        'nochmod',
        'allowuserfxp',
        'allowanonymousfxp',
        'prohibitdotfileswrite',
        'prohibitdotfilesread',
        'allowdotfiles',
    ]

    def __init__(self, wrt):
        super(PureFTP, self).__init__(wrt=wrt)
        JSBASE.__init__(self)

    @property
    def section(self):
        sections = self.package.find(PureFTP.SECTION)
        if not sections:
            section = self.package.add(PureFTP.SECTION)
        else:
            section = sections[0]

        return section

    def commit(self):
        self._wrt.commit(self.package)
        con = self._wrt.connection
        with settings(shell=self._wrt.WRT_SHELL, warn_only=not self.enabled,
                      abort_exception=PureFTPError):
            # restart ftp
            con.run('/etc/init.d/pure-ftpd restart')
