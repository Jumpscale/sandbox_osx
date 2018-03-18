
from JumpScale9.core.JSBase import JSBase
import os
os.environ["LC_ALL"]='en_US.UTF-8'
from JumpScale9 import j


class clients:

    def __init__(self):
        self._tarantool = None
        self._redis = None
        self._ssh = None
        self._http = None
        self._sshkey = None
        self._git = None
        self._syncthing = None
        self._postgres = None
        self._zero_os = None
        self._s3 = None
        self._zerohub = None
        self._portal = None
        self._ovh = None
        self._oauth = None
        self._redis_config = None
        self._telegram_bot = None
        self._mongodb = None
        self._currencylayer = None
        self._wordpress = None
        self._agentcontroller = None
        self._ays = None
        self._sendgrid = None
        self._email = None
        self._openvcloud = None
        self._intercom = None
        self._erppeek = None
        self._itsyouonline = None
        self._grafana = None
        self._zerostor = None
        self._influxdb = None
        self._sqlalchemy = None
        self._racktivity = None
        self._gitea = None
        self._github = None
        self._google_compute = None
        self._peewee = None
        self._rogerthat = None
        self._mysql = None
        self._etcd = None
        self._celery = None
        self._kraken = None
        self._zerotier = None
        self._kubernetes = None
        self._coredns = None
        self._gogs = None
        self._graphite = None
        self._matrix = None
        self._zrobot = None
        self._packetnet = None
        self._whmcs = None
        self._zdb = None

    @property
    def tarantool(self):
        if self._tarantool is None:
            # print("PROP:tarantool")
            from JumpScale9.clients.tarantool.TarantoolFactory import TarantoolFactory as TarantoolFactory
            self._tarantool = TarantoolFactory()
        return self._tarantool

    @property
    def redis(self):
        if self._redis is None:
            # print("PROP:redis")
            from JumpScale9.clients.redis.RedisFactory import RedisFactory as RedisFactory
            self._redis = RedisFactory()
        return self._redis

    @property
    def ssh(self):
        if self._ssh is None:
            # print("PROP:ssh")
            from JumpScale9.clients.ssh.SSHClientFactory import SSHClientFactory as SSHClientFactory
            self._ssh = SSHClientFactory()
        return self._ssh

    @property
    def http(self):
        if self._http is None:
            # print("PROP:http")
            from JumpScale9.clients.http.HttpClient import HttpClient as HttpClient
            self._http = HttpClient()
        return self._http

    @property
    def sshkey(self):
        if self._sshkey is None:
            # print("PROP:sshkey")
            from JumpScale9.clients.sshkey.SSHKeys import SSHKeys as SSHKeys
            self._sshkey = SSHKeys()
        return self._sshkey

    @property
    def git(self):
        if self._git is None:
            # print("PROP:git")
            from JumpScale9.clients.git.GitFactory import GitFactory as GitFactory
            self._git = GitFactory()
        return self._git

    @property
    def syncthing(self):
        if self._syncthing is None:
            # print("PROP:syncthing")
            from JumpScale9Lib.clients.syncthing.Syncthing import SyncthingFactory as SyncthingFactory
            self._syncthing = SyncthingFactory()
        return self._syncthing

    @property
    def postgres(self):
        if self._postgres is None:
            # print("PROP:postgres")
            from JumpScale9Lib.clients.postgresql.PostgresqlFactory import PostgresqlFactory as PostgresqlFactory
            self._postgres = PostgresqlFactory()
        return self._postgres

    @property
    def zero_os(self):
        if self._zero_os is None:
            # print("PROP:zero_os")
            from JumpScale9Lib.clients.zero_os.ZeroOSFactory import ZeroOSFactory as ZeroOSFactory
            self._zero_os = ZeroOSFactory()
        return self._zero_os

    @property
    def s3(self):
        if self._s3 is None:
            # print("PROP:s3")
            from JumpScale9Lib.clients.s3.S3Factory import S3Factory as S3Factory
            self._s3 = S3Factory()
        return self._s3

    @property
    def zerohub(self):
        if self._zerohub is None:
            # print("PROP:zerohub")
            from JumpScale9Lib.clients.zero_hub.ZeroHubFactory import ZeroHubFactory as ZeroHubFactory
            self._zerohub = ZeroHubFactory()
        return self._zerohub

    @property
    def portal(self):
        if self._portal is None:
            # print("PROP:portal")
            from JumpScale9Lib.clients.portal.PortalClientFactory import PortalClientFactory as PortalClientFactory
            self._portal = PortalClientFactory()
        return self._portal

    @property
    def ovh(self):
        if self._ovh is None:
            # print("PROP:ovh")
            from JumpScale9Lib.clients.ovh.OVHFactory import OVHFactory as OVHFactory
            self._ovh = OVHFactory()
        return self._ovh

    @property
    def oauth(self):
        if self._oauth is None:
            # print("PROP:oauth")
            from JumpScale9Lib.clients.oauth.OauthFactory import OauthFactory as OauthFactory
            self._oauth = OauthFactory()
        return self._oauth

    @property
    def redis_config(self):
        if self._redis_config is None:
            # print("PROP:redis_config")
            from JumpScale9Lib.clients.redisconfig.RedisConfigFactory import RedisConfigFactory as RedisConfigFactory
            self._redis_config = RedisConfigFactory()
        return self._redis_config

    @property
    def telegram_bot(self):
        if self._telegram_bot is None:
            # print("PROP:telegram_bot")
            from JumpScale9Lib.clients.telegram_bot.TelegramBot import TelegramBotFactory as TelegramBotFactory
            self._telegram_bot = TelegramBotFactory()
        return self._telegram_bot

    @property
    def mongodb(self):
        if self._mongodb is None:
            # print("PROP:mongodb")
            from JumpScale9Lib.clients.mongodbclient.MongoDBClient import MongoClientFactory as MongoClientFactory
            self._mongodb = MongoClientFactory()
        return self._mongodb

    @property
    def currencylayer(self):
        if self._currencylayer is None:
            # print("PROP:currencylayer")
            from JumpScale9Lib.clients.currencylayer.CurrencyLayer import CurrencyLayer as CurrencyLayer
            self._currencylayer = CurrencyLayer()
        return self._currencylayer

    @property
    def wordpress(self):
        if self._wordpress is None:
            # print("PROP:wordpress")
            from JumpScale9Lib.clients.wordpress.WordpressFactory import WordpressFactory as WordpressFactory
            self._wordpress = WordpressFactory()
        return self._wordpress

    @property
    def agentcontroller(self):
        if self._agentcontroller is None:
            # print("PROP:agentcontroller")
            from JumpScale9Lib.clients.agentcontroller.Client import ACFactory as ACFactory
            self._agentcontroller = ACFactory()
        return self._agentcontroller

    @property
    def ays(self):
        if self._ays is None:
            # print("PROP:ays")
            from JumpScale9Lib.clients.atyourservice.ays.ClientFactory import ClientFactory as ClientFactory
            self._ays = ClientFactory()
        return self._ays

    @property
    def sendgrid(self):
        if self._sendgrid is None:
            # print("PROP:sendgrid")
            from JumpScale9Lib.clients.mail.sendgrid.SendGridClient import SendGridClient as SendGridClient
            self._sendgrid = SendGridClient()
        return self._sendgrid

    @property
    def email(self):
        if self._email is None:
            # print("PROP:email")
            from JumpScale9Lib.clients.mail.EmailClient import EmailClientFactory as EmailClientFactory
            self._email = EmailClientFactory()
        return self._email

    @property
    def openvcloud(self):
        if self._openvcloud is None:
            # print("PROP:openvcloud")
            from JumpScale9Lib.clients.openvcloud.OVCFactory import OVCClientFactory as OVCClientFactory
            self._openvcloud = OVCClientFactory()
        return self._openvcloud

    @property
    def intercom(self):
        if self._intercom is None:
            # print("PROP:intercom")
            from JumpScale9Lib.clients.intercom.Intercom import Intercom as Intercom
            self._intercom = Intercom()
        return self._intercom

    @property
    def erppeek(self):
        if self._erppeek is None:
            # print("PROP:erppeek")
            from JumpScale9Lib.clients.erppeek.Erppeek import ErppeekFactory as ErppeekFactory
            self._erppeek = ErppeekFactory()
        return self._erppeek

    @property
    def itsyouonline(self):
        if self._itsyouonline is None:
            # print("PROP:itsyouonline")
            from JumpScale9Lib.clients.itsyouonline.IYOFactory import IYOFactory as IYOFactory
            self._itsyouonline = IYOFactory()
        return self._itsyouonline

    @property
    def grafana(self):
        if self._grafana is None:
            # print("PROP:grafana")
            from JumpScale9Lib.clients.grafana.Grafana import GrafanaFactory as GrafanaFactory
            self._grafana = GrafanaFactory()
        return self._grafana

    @property
    def zerostor(self):
        if self._zerostor is None:
            # print("PROP:zerostor")
            from JumpScale9Lib.clients.zero_stor.ZeroStorFactory import ZeroStorFactory as ZeroStorFactory
            self._zerostor = ZeroStorFactory()
        return self._zerostor

    @property
    def influxdb(self):
        if self._influxdb is None:
            # print("PROP:influxdb")
            from JumpScale9Lib.clients.influxdb_.Influxdb import InfluxdbFactory as InfluxdbFactory
            self._influxdb = InfluxdbFactory()
        return self._influxdb

    @property
    def sqlalchemy(self):
        if self._sqlalchemy is None:
            # print("PROP:sqlalchemy")
            from JumpScale9Lib.clients.sqlalchemy.SQLAlchemy import SQLAlchemyFactory as SQLAlchemyFactory
            self._sqlalchemy = SQLAlchemyFactory()
        return self._sqlalchemy

    @property
    def racktivity(self):
        if self._racktivity is None:
            # print("PROP:racktivity")
            from JumpScale9Lib.clients.racktivity.RacktivityFactory import RacktivityFactory as RacktivityFactory
            self._racktivity = RacktivityFactory()
        return self._racktivity

    @property
    def gitea(self):
        if self._gitea is None:
            # print("PROP:gitea")
            from JumpScale9Lib.clients.gitea.GiteaFactory import GiteaFactory as GiteaFactory
            self._gitea = GiteaFactory()
        return self._gitea

    @property
    def github(self):
        if self._github is None:
            # print("PROP:github")
            from JumpScale9Lib.clients.github.Github import GitHubFactory as GitHubFactory
            self._github = GitHubFactory()
        return self._github

    @property
    def google_compute(self):
        if self._google_compute is None:
            # print("PROP:google_compute")
            from JumpScale9Lib.clients.google_compute.GoogleCompute import GoogleCompute as GoogleCompute
            self._google_compute = GoogleCompute()
        return self._google_compute

    @property
    def peewee(self):
        if self._peewee is None:
            # print("PROP:peewee")
            from JumpScale9Lib.clients.peewee.PeeweeFactory import PeeweeFactory as PeeweeFactory
            self._peewee = PeeweeFactory()
        return self._peewee

    @property
    def rogerthat(self):
        if self._rogerthat is None:
            # print("PROP:rogerthat")
            from JumpScale9Lib.clients.rogerthat.Rogerthat import RogerthatFactory as RogerthatFactory
            self._rogerthat = RogerthatFactory()
        return self._rogerthat

    @property
    def mysql(self):
        if self._mysql is None:
            # print("PROP:mysql")
            from JumpScale9Lib.clients.mysql.MySQLFactory import MySQLFactory as MySQLFactory
            self._mysql = MySQLFactory()
        return self._mysql

    @property
    def etcd(self):
        if self._etcd is None:
            # print("PROP:etcd")
            from JumpScale9Lib.clients.etcd.EtcdFactory import EtcdFactory as EtcdFactory
            self._etcd = EtcdFactory()
        return self._etcd

    @property
    def celery(self):
        if self._celery is None:
            # print("PROP:celery")
            from JumpScale9Lib.clients.celery.CeleryFactory import CeleryFactory as CeleryFactory
            self._celery = CeleryFactory()
        return self._celery

    @property
    def kraken(self):
        if self._kraken is None:
            # print("PROP:kraken")
            from JumpScale9Lib.clients.kraken.Kraken import Kraken as Kraken
            self._kraken = Kraken()
        return self._kraken

    @property
    def zerotier(self):
        if self._zerotier is None:
            # print("PROP:zerotier")
            from JumpScale9Lib.clients.zerotier.ZerotierFactory import ZerotierFactory as ZerotierFactory
            self._zerotier = ZerotierFactory()
        return self._zerotier

    @property
    def kubernetes(self):
        if self._kubernetes is None:
            # print("PROP:kubernetes")
            from JumpScale9Lib.clients.kubernetes.KubernetesFactory import KubernetesFactory as KubernetesFactory
            self._kubernetes = KubernetesFactory()
        return self._kubernetes

    @property
    def coredns(self):
        if self._coredns is None:
            # print("PROP:coredns")
            from JumpScale9Lib.clients.coredns.CorednsFactory import CorednsFactory as CorednsFactory
            self._coredns = CorednsFactory()
        return self._coredns

    @property
    def gogs(self):
        if self._gogs is None:
            # print("PROP:gogs")
            from JumpScale9Lib.clients.gogs.GogsFactory import GogsFactory as GogsFactory
            self._gogs = GogsFactory()
        return self._gogs

    @property
    def graphite(self):
        if self._graphite is None:
            # print("PROP:graphite")
            from JumpScale9Lib.clients.graphite.GraphiteClient import GraphiteFactory as GraphiteFactory
            self._graphite = GraphiteFactory()
        return self._graphite

    @property
    def matrix(self):
        if self._matrix is None:
            # print("PROP:matrix")
            from JumpScale9Lib.clients.matrix.MatrixFactory import MatrixFactory as MatrixFactory
            self._matrix = MatrixFactory()
        return self._matrix

    @property
    def zrobot(self):
        if self._zrobot is None:
            # print("PROP:zrobot")
            from JumpScale9Lib.clients.zerorobot.ZeroRobotFactory import ZeroRobotFactory as ZeroRobotFactory
            self._zrobot = ZeroRobotFactory()
        return self._zrobot

    @property
    def packetnet(self):
        if self._packetnet is None:
            # print("PROP:packetnet")
            from JumpScale9Lib.clients.packetnet.PacketNetFactory import PacketNetFactory as PacketNetFactory
            self._packetnet = PacketNetFactory()
        return self._packetnet

    @property
    def whmcs(self):
        if self._whmcs is None:
            # print("PROP:whmcs")
            from JumpScale9Lib.clients.whmcs.WhmcsFactory import WhmcsFactory as WhmcsFactory
            self._whmcs = WhmcsFactory()
        return self._whmcs

    @property
    def zdb(self):
        if self._zdb is None:
            # print("PROP:zdb")
            from JumpScale9RecordChain.clients.zdb.ZDBFactory import ZDBFactory as ZDBFactory
            self._zdb = ZDBFactory()
        return self._zdb


if not hasattr(j.clients,"tarantool"):
    j.clients._tarantool = None
    j.clients.__class__.tarantool = clients.tarantool
if not hasattr(j.clients,"redis"):
    j.clients._redis = None
    j.clients.__class__.redis = clients.redis
if not hasattr(j.clients,"ssh"):
    j.clients._ssh = None
    j.clients.__class__.ssh = clients.ssh
if not hasattr(j.clients,"http"):
    j.clients._http = None
    j.clients.__class__.http = clients.http
if not hasattr(j.clients,"sshkey"):
    j.clients._sshkey = None
    j.clients.__class__.sshkey = clients.sshkey
if not hasattr(j.clients,"git"):
    j.clients._git = None
    j.clients.__class__.git = clients.git
if not hasattr(j.clients,"syncthing"):
    j.clients._syncthing = None
    j.clients.__class__.syncthing = clients.syncthing
if not hasattr(j.clients,"postgres"):
    j.clients._postgres = None
    j.clients.__class__.postgres = clients.postgres
if not hasattr(j.clients,"zero_os"):
    j.clients._zero_os = None
    j.clients.__class__.zero_os = clients.zero_os
if not hasattr(j.clients,"s3"):
    j.clients._s3 = None
    j.clients.__class__.s3 = clients.s3
if not hasattr(j.clients,"zerohub"):
    j.clients._zerohub = None
    j.clients.__class__.zerohub = clients.zerohub
if not hasattr(j.clients,"portal"):
    j.clients._portal = None
    j.clients.__class__.portal = clients.portal
if not hasattr(j.clients,"ovh"):
    j.clients._ovh = None
    j.clients.__class__.ovh = clients.ovh
if not hasattr(j.clients,"oauth"):
    j.clients._oauth = None
    j.clients.__class__.oauth = clients.oauth
if not hasattr(j.clients,"redis_config"):
    j.clients._redis_config = None
    j.clients.__class__.redis_config = clients.redis_config
if not hasattr(j.clients,"telegram_bot"):
    j.clients._telegram_bot = None
    j.clients.__class__.telegram_bot = clients.telegram_bot
if not hasattr(j.clients,"mongodb"):
    j.clients._mongodb = None
    j.clients.__class__.mongodb = clients.mongodb
if not hasattr(j.clients,"currencylayer"):
    j.clients._currencylayer = None
    j.clients.__class__.currencylayer = clients.currencylayer
if not hasattr(j.clients,"wordpress"):
    j.clients._wordpress = None
    j.clients.__class__.wordpress = clients.wordpress
if not hasattr(j.clients,"agentcontroller"):
    j.clients._agentcontroller = None
    j.clients.__class__.agentcontroller = clients.agentcontroller
if not hasattr(j.clients,"ays"):
    j.clients._ays = None
    j.clients.__class__.ays = clients.ays
if not hasattr(j.clients,"sendgrid"):
    j.clients._sendgrid = None
    j.clients.__class__.sendgrid = clients.sendgrid
if not hasattr(j.clients,"email"):
    j.clients._email = None
    j.clients.__class__.email = clients.email
if not hasattr(j.clients,"openvcloud"):
    j.clients._openvcloud = None
    j.clients.__class__.openvcloud = clients.openvcloud
if not hasattr(j.clients,"intercom"):
    j.clients._intercom = None
    j.clients.__class__.intercom = clients.intercom
if not hasattr(j.clients,"erppeek"):
    j.clients._erppeek = None
    j.clients.__class__.erppeek = clients.erppeek
if not hasattr(j.clients,"itsyouonline"):
    j.clients._itsyouonline = None
    j.clients.__class__.itsyouonline = clients.itsyouonline
if not hasattr(j.clients,"grafana"):
    j.clients._grafana = None
    j.clients.__class__.grafana = clients.grafana
if not hasattr(j.clients,"zerostor"):
    j.clients._zerostor = None
    j.clients.__class__.zerostor = clients.zerostor
if not hasattr(j.clients,"influxdb"):
    j.clients._influxdb = None
    j.clients.__class__.influxdb = clients.influxdb
if not hasattr(j.clients,"sqlalchemy"):
    j.clients._sqlalchemy = None
    j.clients.__class__.sqlalchemy = clients.sqlalchemy
if not hasattr(j.clients,"racktivity"):
    j.clients._racktivity = None
    j.clients.__class__.racktivity = clients.racktivity
if not hasattr(j.clients,"gitea"):
    j.clients._gitea = None
    j.clients.__class__.gitea = clients.gitea
if not hasattr(j.clients,"github"):
    j.clients._github = None
    j.clients.__class__.github = clients.github
if not hasattr(j.clients,"google_compute"):
    j.clients._google_compute = None
    j.clients.__class__.google_compute = clients.google_compute
if not hasattr(j.clients,"peewee"):
    j.clients._peewee = None
    j.clients.__class__.peewee = clients.peewee
if not hasattr(j.clients,"rogerthat"):
    j.clients._rogerthat = None
    j.clients.__class__.rogerthat = clients.rogerthat
if not hasattr(j.clients,"mysql"):
    j.clients._mysql = None
    j.clients.__class__.mysql = clients.mysql
if not hasattr(j.clients,"etcd"):
    j.clients._etcd = None
    j.clients.__class__.etcd = clients.etcd
if not hasattr(j.clients,"celery"):
    j.clients._celery = None
    j.clients.__class__.celery = clients.celery
if not hasattr(j.clients,"kraken"):
    j.clients._kraken = None
    j.clients.__class__.kraken = clients.kraken
if not hasattr(j.clients,"zerotier"):
    j.clients._zerotier = None
    j.clients.__class__.zerotier = clients.zerotier
if not hasattr(j.clients,"kubernetes"):
    j.clients._kubernetes = None
    j.clients.__class__.kubernetes = clients.kubernetes
if not hasattr(j.clients,"coredns"):
    j.clients._coredns = None
    j.clients.__class__.coredns = clients.coredns
if not hasattr(j.clients,"gogs"):
    j.clients._gogs = None
    j.clients.__class__.gogs = clients.gogs
if not hasattr(j.clients,"graphite"):
    j.clients._graphite = None
    j.clients.__class__.graphite = clients.graphite
if not hasattr(j.clients,"matrix"):
    j.clients._matrix = None
    j.clients.__class__.matrix = clients.matrix
if not hasattr(j.clients,"zrobot"):
    j.clients._zrobot = None
    j.clients.__class__.zrobot = clients.zrobot
if not hasattr(j.clients,"packetnet"):
    j.clients._packetnet = None
    j.clients.__class__.packetnet = clients.packetnet
if not hasattr(j.clients,"whmcs"):
    j.clients._whmcs = None
    j.clients.__class__.whmcs = clients.whmcs
if not hasattr(j.clients,"zdb"):
    j.clients._zdb = None
    j.clients.__class__.zdb = clients.zdb


 

class tools:

    def __init__(self):
        self._myconfig = None
        self._develop = None
        self._nodemgr = None
        self._performancetrace = None
        self._configmanager = None
        self._path = None
        self._lock = None
        self._cython = None
        self._bash = None
        self._formbuilder = None
        self._tmux = None
        self._executor = None
        self._executorLocal = None
        self._perftesttools = None
        self._zerorobot = None
        self._console = None
        self._tarfile = None
        self._zipfile = None
        self._numtools = None
        self._email = None
        self._sandboxer = None
        self._inifile = None
        self._itenv_manager = None
        self._imagelib = None
        self._markdown = None
        self._offliner = None
        self._aggregator = None
        self._realityprocess = None
        self._timer = None
        self._async = None
        self._packInCode = None
        self._js8stub = None
        self._byteprocessor = None
        self._team_manager = None
        self._objectinspector = None
        self._testengine = None
        self._docgenerator = None
        self._raml = None
        self._code = None
        self._dnstools = None
        self._typechecker = None
        self._issuemanager = None
        self._expect = None
        self._tls = None
        self._wic = None
        self._flist = None
        self._html = None
        self._prefab = None

    @property
    def myconfig(self):
        if self._myconfig is None:
            # print("PROP:myconfig")
            from JumpScale9.tools.myconfig.MyConfig import MyConfig as MyConfig
            self._myconfig = MyConfig()
        return self._myconfig

    @property
    def develop(self):
        if self._develop is None:
            # print("PROP:develop")
            from JumpScale9.tools.develop.DevelopTools import DevelopToolsFactory as DevelopToolsFactory
            self._develop = DevelopToolsFactory()
        return self._develop

    @property
    def nodemgr(self):
        if self._nodemgr is None:
            # print("PROP:nodemgr")
            from JumpScale9.tools.nodemgr.Nodes import Nodes as Nodes
            self._nodemgr = Nodes()
        return self._nodemgr

    @property
    def performancetrace(self):
        if self._performancetrace is None:
            # print("PROP:performancetrace")
            from JumpScale9.tools.performancetrace.PerformanceTrace import PerformanceTraceFactory as PerformanceTraceFactory
            self._performancetrace = PerformanceTraceFactory()
        return self._performancetrace

    @property
    def configmanager(self):
        if self._configmanager is None:
            # print("PROP:configmanager")
            from JumpScale9.tools.configmanager.ConfigManager import ConfigFactory as ConfigFactory
            self._configmanager = ConfigFactory()
        return self._configmanager

    @property
    def path(self):
        if self._path is None:
            # print("PROP:path")
            from JumpScale9.tools.path.PathFactory import PathFactory as PathFactory
            self._path = PathFactory()
        return self._path

    @property
    def lock(self):
        if self._lock is None:
            # print("PROP:lock")
            from JumpScale9.tools.lock.Lock import LockFactory as LockFactory
            self._lock = LockFactory()
        return self._lock

    @property
    def cython(self):
        if self._cython is None:
            # print("PROP:cython")
            from JumpScale9.tools.cython.CythonFactory import CythonFactory as CythonFactory
            self._cython = CythonFactory()
        return self._cython

    @property
    def bash(self):
        if self._bash is None:
            # print("PROP:bash")
            from JumpScale9.tools.bash.BashFactory import BashFactory as BashFactory
            self._bash = BashFactory()
        return self._bash

    @property
    def formbuilder(self):
        if self._formbuilder is None:
            # print("PROP:formbuilder")
            from JumpScale9.tools.formbuilder.FormBuilder import FormBuilderFactory as FormBuilderFactory
            self._formbuilder = FormBuilderFactory()
        return self._formbuilder

    @property
    def tmux(self):
        if self._tmux is None:
            # print("PROP:tmux")
            from JumpScale9.tools.tmux.Tmux import Tmux as Tmux
            self._tmux = Tmux()
        return self._tmux

    @property
    def executor(self):
        if self._executor is None:
            # print("PROP:executor")
            from JumpScale9.tools.executor.ExecutorFactory import ExecutorFactory as ExecutorFactory
            self._executor = ExecutorFactory()
        return self._executor

    @property
    def executorLocal(self):
        if self._executorLocal is None:
            # print("PROP:executorLocal")
            from JumpScale9.tools.executor.ExecutorLocal import ExecutorLocal as ExecutorLocal
            self._executorLocal = ExecutorLocal()
        return self._executorLocal

    @property
    def perftesttools(self):
        if self._perftesttools is None:
            # print("PROP:perftesttools")
            from JumpScale9.tools.perftesttools.PerfTestToolsFactory import PerfTestToolsFactory as PerfTestToolsFactory
            self._perftesttools = PerfTestToolsFactory()
        return self._perftesttools

    @property
    def zerorobot(self):
        if self._zerorobot is None:
            # print("PROP:zerorobot")
            from JumpScale9.tools.zerorobot.ZeroRobot import ZeroRobot as ZeroRobot
            self._zerorobot = ZeroRobot()
        return self._zerorobot

    @property
    def console(self):
        if self._console is None:
            # print("PROP:console")
            from JumpScale9.tools.console.Console import Console as Console
            self._console = Console()
        return self._console

    @property
    def tarfile(self):
        if self._tarfile is None:
            # print("PROP:tarfile")
            from JumpScale9.data.tarfile.TarFile import TarFileFactory as TarFileFactory
            self._tarfile = TarFileFactory()
        return self._tarfile

    @property
    def zipfile(self):
        if self._zipfile is None:
            # print("PROP:zipfile")
            from JumpScale9.data.zip.ZipFile import ZipFileFactory as ZipFileFactory
            self._zipfile = ZipFileFactory()
        return self._zipfile

    @property
    def numtools(self):
        if self._numtools is None:
            # print("PROP:numtools")
            from JumpScale9.data.numtools.NumTools import NumTools as NumTools
            self._numtools = NumTools()
        return self._numtools

    @property
    def email(self):
        if self._email is None:
            # print("PROP:email")
            from JumpScale9.data.email.Email import EmailTool as EmailTool
            self._email = EmailTool()
        return self._email

    @property
    def sandboxer(self):
        if self._sandboxer is None:
            # print("PROP:sandboxer")
            from JumpScale9Lib.tools.sandboxer.Sandboxer import Sandboxer as Sandboxer
            self._sandboxer = Sandboxer()
        return self._sandboxer

    @property
    def inifile(self):
        if self._inifile is None:
            # print("PROP:inifile")
            from JumpScale9Lib.tools.inifile.IniFile import InifileTool as InifileTool
            self._inifile = InifileTool()
        return self._inifile

    @property
    def itenv_manager(self):
        if self._itenv_manager is None:
            # print("PROP:itenv_manager")
            from JumpScale9Lib.tools.itenvmgr.ITEnvManager import ITEnvManager as ITEnvManager
            self._itenv_manager = ITEnvManager()
        return self._itenv_manager

    @property
    def imagelib(self):
        if self._imagelib is None:
            # print("PROP:imagelib")
            from JumpScale9Lib.tools.imagelib.ImageLib import ImageLib as ImageLib
            self._imagelib = ImageLib()
        return self._imagelib

    @property
    def markdown(self):
        if self._markdown is None:
            # print("PROP:markdown")
            from JumpScale9Lib.tools.markdown.MarkDown import MarkDown as MarkDown
            self._markdown = MarkDown()
        return self._markdown

    @property
    def offliner(self):
        if self._offliner is None:
            # print("PROP:offliner")
            from JumpScale9Lib.tools.offliner.Offliner import Offliner as Offliner
            self._offliner = Offliner()
        return self._offliner

    @property
    def aggregator(self):
        if self._aggregator is None:
            # print("PROP:aggregator")
            from JumpScale9Lib.tools.aggregator.Aggregator import Aggregator as Aggregator
            self._aggregator = Aggregator()
        return self._aggregator

    @property
    def realityprocess(self):
        if self._realityprocess is None:
            # print("PROP:realityprocess")
            from JumpScale9Lib.tools.aggregator.RealityProcess import RealitProcess as RealitProcess
            self._realityprocess = RealitProcess()
        return self._realityprocess

    @property
    def timer(self):
        if self._timer is None:
            # print("PROP:timer")
            from JumpScale9Lib.tools.timer.Timer import TIMER as TIMER
            self._timer = TIMER()
        return self._timer

    @property
    def async(self):
        if self._async is None:
            # print("PROP:async")
            from JumpScale9Lib.tools.async.AsyncToolFactory import AsyncTool as AsyncTool
            self._async = AsyncTool()
        return self._async

    @property
    def packInCode(self):
        if self._packInCode is None:
            # print("PROP:packInCode")
            from JumpScale9Lib.tools.packInCode.PackInCode import packInCodeFactory as packInCodeFactory
            self._packInCode = packInCodeFactory()
        return self._packInCode

    @property
    def js8stub(self):
        if self._js8stub is None:
            # print("PROP:js8stub")
            from JumpScale9Lib.tools.js8stub.JS8Stub import JS8Stub as JS8Stub
            self._js8stub = JS8Stub()
        return self._js8stub

    @property
    def byteprocessor(self):
        if self._byteprocessor is None:
            # print("PROP:byteprocessor")
            from JumpScale9Lib.tools.byteprocessor.ByteProcessor import ByteProcessor as ByteProcessor
            self._byteprocessor = ByteProcessor()
        return self._byteprocessor

    @property
    def team_manager(self):
        if self._team_manager is None:
            # print("PROP:team_manager")
            from JumpScale9Lib.tools.teammgr.Teammgr import Teammgr as Teammgr
            self._team_manager = Teammgr()
        return self._team_manager

    @property
    def objectinspector(self):
        if self._objectinspector is None:
            # print("PROP:objectinspector")
            from JumpScale9Lib.tools.objectinspector.ObjectInspector import ObjectInspector as ObjectInspector
            self._objectinspector = ObjectInspector()
        return self._objectinspector

    @property
    def testengine(self):
        if self._testengine is None:
            # print("PROP:testengine")
            from JumpScale9Lib.tools.testengine.TestEngine import TestEngine as TestEngine
            self._testengine = TestEngine()
        return self._testengine

    @property
    def docgenerator(self):
        if self._docgenerator is None:
            # print("PROP:docgenerator")
            from JumpScale9Lib.tools.docgenerator.DocGenerator import DocGenerator as DocGenerator
            self._docgenerator = DocGenerator()
        return self._docgenerator

    @property
    def raml(self):
        if self._raml is None:
            # print("PROP:raml")
            from JumpScale9Lib.tools.raml.RamlToolsFactory import RamlToolsFactory as RamlToolsFactory
            self._raml = RamlToolsFactory()
        return self._raml

    @property
    def code(self):
        if self._code is None:
            # print("PROP:code")
            from JumpScale9Lib.tools.codetools.CodeTools import CodeTools as CodeTools
            self._code = CodeTools()
        return self._code

    @property
    def dnstools(self):
        if self._dnstools is None:
            # print("PROP:dnstools")
            from JumpScale9Lib.tools.dns.DNSTools import DNSTools as DNSTools
            self._dnstools = DNSTools()
        return self._dnstools

    @property
    def typechecker(self):
        if self._typechecker is None:
            # print("PROP:typechecker")
            from JumpScale9Lib.tools.typechecker.TypeChecker import TypeCheckerFactory as TypeCheckerFactory
            self._typechecker = TypeCheckerFactory()
        return self._typechecker

    @property
    def issuemanager(self):
        if self._issuemanager is None:
            # print("PROP:issuemanager")
            from JumpScale9Lib.tools.issuemanager.IssueManager import IssueManager as IssueManager
            self._issuemanager = IssueManager()
        return self._issuemanager

    @property
    def expect(self):
        if self._expect is None:
            # print("PROP:expect")
            from JumpScale9Lib.tools.expect.Expect import ExpectTool as ExpectTool
            self._expect = ExpectTool()
        return self._expect

    @property
    def tls(self):
        if self._tls is None:
            # print("PROP:tls")
            from JumpScale9Lib.sal.tls.TLSFactory import TLSFactory as TLSFactory
            self._tls = TLSFactory()
        return self._tls

    @property
    def wic(self):
        if self._wic is None:
            # print("PROP:wic")
            from JumpScale9Lib.sal.wic.WIC_Factory import WIC_Factory as WIC_Factory
            self._wic = WIC_Factory()
        return self._wic

    @property
    def flist(self):
        if self._flist is None:
            # print("PROP:flist")
            from JumpScale9Lib.data.flist.FListFactory import FListFactory as FListFactory
            self._flist = FListFactory()
        return self._flist

    @property
    def html(self):
        if self._html is None:
            # print("PROP:html")
            from JumpScale9Lib.data.html.HTMLFactory import HTMLFactory as HTMLFactory
            self._html = HTMLFactory()
        return self._html

    @property
    def prefab(self):
        if self._prefab is None:
            # print("PROP:prefab")
            from JumpScale9Prefab.PrefabFactory import PrefabRootClassFactory as PrefabRootClassFactory
            self._prefab = PrefabRootClassFactory()
        return self._prefab


if not hasattr(j.tools,"myconfig"):
    j.tools._myconfig = None
    j.tools.__class__.myconfig = tools.myconfig
if not hasattr(j.tools,"develop"):
    j.tools._develop = None
    j.tools.__class__.develop = tools.develop
if not hasattr(j.tools,"nodemgr"):
    j.tools._nodemgr = None
    j.tools.__class__.nodemgr = tools.nodemgr
if not hasattr(j.tools,"performancetrace"):
    j.tools._performancetrace = None
    j.tools.__class__.performancetrace = tools.performancetrace
if not hasattr(j.tools,"configmanager"):
    j.tools._configmanager = None
    j.tools.__class__.configmanager = tools.configmanager
if not hasattr(j.tools,"path"):
    j.tools._path = None
    j.tools.__class__.path = tools.path
if not hasattr(j.tools,"lock"):
    j.tools._lock = None
    j.tools.__class__.lock = tools.lock
if not hasattr(j.tools,"cython"):
    j.tools._cython = None
    j.tools.__class__.cython = tools.cython
if not hasattr(j.tools,"bash"):
    j.tools._bash = None
    j.tools.__class__.bash = tools.bash
if not hasattr(j.tools,"formbuilder"):
    j.tools._formbuilder = None
    j.tools.__class__.formbuilder = tools.formbuilder
if not hasattr(j.tools,"tmux"):
    j.tools._tmux = None
    j.tools.__class__.tmux = tools.tmux
if not hasattr(j.tools,"executor"):
    j.tools._executor = None
    j.tools.__class__.executor = tools.executor
if not hasattr(j.tools,"executorLocal"):
    j.tools._executorLocal = None
    j.tools.__class__.executorLocal = tools.executorLocal
if not hasattr(j.tools,"perftesttools"):
    j.tools._perftesttools = None
    j.tools.__class__.perftesttools = tools.perftesttools
if not hasattr(j.tools,"zerorobot"):
    j.tools._zerorobot = None
    j.tools.__class__.zerorobot = tools.zerorobot
if not hasattr(j.tools,"console"):
    j.tools._console = None
    j.tools.__class__.console = tools.console
if not hasattr(j.tools,"tarfile"):
    j.tools._tarfile = None
    j.tools.__class__.tarfile = tools.tarfile
if not hasattr(j.tools,"zipfile"):
    j.tools._zipfile = None
    j.tools.__class__.zipfile = tools.zipfile
if not hasattr(j.tools,"numtools"):
    j.tools._numtools = None
    j.tools.__class__.numtools = tools.numtools
if not hasattr(j.tools,"email"):
    j.tools._email = None
    j.tools.__class__.email = tools.email
if not hasattr(j.tools,"sandboxer"):
    j.tools._sandboxer = None
    j.tools.__class__.sandboxer = tools.sandboxer
if not hasattr(j.tools,"inifile"):
    j.tools._inifile = None
    j.tools.__class__.inifile = tools.inifile
if not hasattr(j.tools,"itenv_manager"):
    j.tools._itenv_manager = None
    j.tools.__class__.itenv_manager = tools.itenv_manager
if not hasattr(j.tools,"imagelib"):
    j.tools._imagelib = None
    j.tools.__class__.imagelib = tools.imagelib
if not hasattr(j.tools,"markdown"):
    j.tools._markdown = None
    j.tools.__class__.markdown = tools.markdown
if not hasattr(j.tools,"offliner"):
    j.tools._offliner = None
    j.tools.__class__.offliner = tools.offliner
if not hasattr(j.tools,"aggregator"):
    j.tools._aggregator = None
    j.tools.__class__.aggregator = tools.aggregator
if not hasattr(j.tools,"realityprocess"):
    j.tools._realityprocess = None
    j.tools.__class__.realityprocess = tools.realityprocess
if not hasattr(j.tools,"timer"):
    j.tools._timer = None
    j.tools.__class__.timer = tools.timer
if not hasattr(j.tools,"async"):
    j.tools._async = None
    j.tools.__class__.async = tools.async
if not hasattr(j.tools,"packInCode"):
    j.tools._packInCode = None
    j.tools.__class__.packInCode = tools.packInCode
if not hasattr(j.tools,"js8stub"):
    j.tools._js8stub = None
    j.tools.__class__.js8stub = tools.js8stub
if not hasattr(j.tools,"byteprocessor"):
    j.tools._byteprocessor = None
    j.tools.__class__.byteprocessor = tools.byteprocessor
if not hasattr(j.tools,"team_manager"):
    j.tools._team_manager = None
    j.tools.__class__.team_manager = tools.team_manager
if not hasattr(j.tools,"objectinspector"):
    j.tools._objectinspector = None
    j.tools.__class__.objectinspector = tools.objectinspector
if not hasattr(j.tools,"testengine"):
    j.tools._testengine = None
    j.tools.__class__.testengine = tools.testengine
if not hasattr(j.tools,"docgenerator"):
    j.tools._docgenerator = None
    j.tools.__class__.docgenerator = tools.docgenerator
if not hasattr(j.tools,"raml"):
    j.tools._raml = None
    j.tools.__class__.raml = tools.raml
if not hasattr(j.tools,"code"):
    j.tools._code = None
    j.tools.__class__.code = tools.code
if not hasattr(j.tools,"dnstools"):
    j.tools._dnstools = None
    j.tools.__class__.dnstools = tools.dnstools
if not hasattr(j.tools,"typechecker"):
    j.tools._typechecker = None
    j.tools.__class__.typechecker = tools.typechecker
if not hasattr(j.tools,"issuemanager"):
    j.tools._issuemanager = None
    j.tools.__class__.issuemanager = tools.issuemanager
if not hasattr(j.tools,"expect"):
    j.tools._expect = None
    j.tools.__class__.expect = tools.expect
if not hasattr(j.tools,"tls"):
    j.tools._tls = None
    j.tools.__class__.tls = tools.tls
if not hasattr(j.tools,"wic"):
    j.tools._wic = None
    j.tools.__class__.wic = tools.wic
if not hasattr(j.tools,"flist"):
    j.tools._flist = None
    j.tools.__class__.flist = tools.flist
if not hasattr(j.tools,"html"):
    j.tools._html = None
    j.tools.__class__.html = tools.html
if not hasattr(j.tools,"prefab"):
    j.tools._prefab = None
    j.tools.__class__.prefab = tools.prefab


 

class sal:

    def __init__(self):
        self._nettools = None
        self._rsync = None
        self._processmanager = None
        self._process = None
        self._fswalker = None
        self._fs = None
        self._docker = None
        self._qemu_img = None
        self._btrfs = None
        self._flist = None
        self._ssl = None
        self._routeros = None
        self._disklayout = None
        self._nic = None
        self._zeronetconfig = None
        self._nfs = None
        self._sshd = None
        self._hostsfile = None
        self._diskmanager = None
        self._aysfs = None
        self._unix = None
        self._samba = None
        self._nginx = None
        self._netconfig = None
        self._kvm = None
        self._ssl_signing = None
        self._windows = None
        self._ufw = None
        self._bind = None
        self._ubuntu = None
        self._openvswitch = None
        self._dnsmasq = None
        self._ciscoswitch = None

    @property
    def nettools(self):
        if self._nettools is None:
            # print("PROP:nettools")
            from JumpScale9.tools.nettools.NetTools import NetTools as NetTools
            self._nettools = NetTools()
        return self._nettools

    @property
    def rsync(self):
        if self._rsync is None:
            # print("PROP:rsync")
            from JumpScale9.sal.rsync.RsyncFactory import RsyncFactory as RsyncFactory
            self._rsync = RsyncFactory()
        return self._rsync

    @property
    def processmanager(self):
        if self._processmanager is None:
            # print("PROP:processmanager")
            from JumpScale9.sal.process.ProcessManagerFactory import ProcessManagerFactory as ProcessManagerFactory
            self._processmanager = ProcessManagerFactory()
        return self._processmanager

    @property
    def process(self):
        if self._process is None:
            # print("PROP:process")
            from JumpScale9.sal.process.SystemProcess import SystemProcess as SystemProcess
            self._process = SystemProcess()
        return self._process

    @property
    def fswalker(self):
        if self._fswalker is None:
            # print("PROP:fswalker")
            from JumpScale9.fs.SystemFSWalker import SystemFSWalker as SystemFSWalker
            self._fswalker = SystemFSWalker()
        return self._fswalker

    @property
    def fs(self):
        if self._fs is None:
            # print("PROP:fs")
            from JumpScale9.fs.SystemFS import SystemFS as SystemFS
            self._fs = SystemFS()
        return self._fs

    @property
    def docker(self):
        if self._docker is None:
            # print("PROP:docker")
            from JumpScale9Lib.tools.docker.Docker import Docker as Docker
            self._docker = Docker()
        return self._docker

    @property
    def qemu_img(self):
        if self._qemu_img is None:
            # print("PROP:qemu_img")
            from JumpScale9Lib.sal.qemu_img.Qemu_img import QemuImg as QemuImg
            self._qemu_img = QemuImg()
        return self._qemu_img

    @property
    def btrfs(self):
        if self._btrfs is None:
            # print("PROP:btrfs")
            from JumpScale9Lib.sal.btrfs.BtrfsExtension import BtfsExtensionFactory as BtfsExtensionFactory
            self._btrfs = BtfsExtensionFactory()
        return self._btrfs

    @property
    def flist(self):
        if self._flist is None:
            # print("PROP:flist")
            from JumpScale9Lib.sal.flist.Flist import Flist as Flist
            self._flist = Flist()
        return self._flist

    @property
    def ssl(self):
        if self._ssl is None:
            # print("PROP:ssl")
            from JumpScale9Lib.sal.ssl.SSL import Empty as Empty
            self._ssl = Empty()
        return self._ssl

    @property
    def routeros(self):
        if self._routeros is None:
            # print("PROP:routeros")
            from JumpScale9Lib.sal.routeros.RouterOS import RouterOSFactory as RouterOSFactory
            self._routeros = RouterOSFactory()
        return self._routeros

    @property
    def disklayout(self):
        if self._disklayout is None:
            # print("PROP:disklayout")
            from JumpScale9Lib.sal.disklayout.DiskManager import DiskManager as DiskManager
            self._disklayout = DiskManager()
        return self._disklayout

    @property
    def nic(self):
        if self._nic is None:
            # print("PROP:nic")
            from JumpScale9Lib.sal.nic.UnixNetworkManager import UnixNetworkManager as UnixNetworkManager
            self._nic = UnixNetworkManager()
        return self._nic

    @property
    def zeronetconfig(self):
        if self._zeronetconfig is None:
            # print("PROP:zeronetconfig")
            from JumpScale9Lib.sal.ZeroNetConfig.ZeroNetConfig import ZeroNetConfig as ZeroNetConfig
            self._zeronetconfig = ZeroNetConfig()
        return self._zeronetconfig

    @property
    def nfs(self):
        if self._nfs is None:
            # print("PROP:nfs")
            from JumpScale9Lib.sal.nfs.NFS import NFSExport as NFSExport
            self._nfs = NFSExport()
        return self._nfs

    @property
    def sshd(self):
        if self._sshd is None:
            # print("PROP:sshd")
            from JumpScale9Lib.sal.sshd.SSHD import SSHD as SSHD
            self._sshd = SSHD()
        return self._sshd

    @property
    def hostsfile(self):
        if self._hostsfile is None:
            # print("PROP:hostsfile")
            from JumpScale9Lib.sal.hostfile.HostFile import HostFileFactory as HostFileFactory
            self._hostsfile = HostFileFactory()
        return self._hostsfile

    @property
    def diskmanager(self):
        if self._diskmanager is None:
            # print("PROP:diskmanager")
            from JumpScale9Lib.sal.diskmanager.Diskmanager import Diskmanager as Diskmanager
            self._diskmanager = Diskmanager()
        return self._diskmanager

    @property
    def aysfs(self):
        if self._aysfs is None:
            # print("PROP:aysfs")
            from JumpScale9Lib.sal.aysfs.AysFs import AysFsFactory as AysFsFactory
            self._aysfs = AysFsFactory()
        return self._aysfs

    @property
    def unix(self):
        if self._unix is None:
            # print("PROP:unix")
            from JumpScale9Lib.sal.unix.Unix import UnixSystem as UnixSystem
            self._unix = UnixSystem()
        return self._unix

    @property
    def samba(self):
        if self._samba is None:
            # print("PROP:samba")
            from JumpScale9Lib.sal.samba.Samba import Samba as Samba
            self._samba = Samba()
        return self._samba

    @property
    def nginx(self):
        if self._nginx is None:
            # print("PROP:nginx")
            from JumpScale9Lib.sal.nginx.Nginx import NginxFactory as NginxFactory
            self._nginx = NginxFactory()
        return self._nginx

    @property
    def netconfig(self):
        if self._netconfig is None:
            # print("PROP:netconfig")
            from JumpScale9Lib.sal.netconfig.Netconfig import Netconfig as Netconfig
            self._netconfig = Netconfig()
        return self._netconfig

    @property
    def kvm(self):
        if self._kvm is None:
            # print("PROP:kvm")
            from JumpScale9Lib.sal.kvm.KVM import KVM as KVM
            self._kvm = KVM()
        return self._kvm

    @property
    def ssl_signing(self):
        if self._ssl_signing is None:
            # print("PROP:ssl_signing")
            from JumpScale9Lib.sal.sslsigning.SSLSigning import SSLSigning as SSLSigning
            self._ssl_signing = SSLSigning()
        return self._ssl_signing

    @property
    def windows(self):
        if self._windows is None:
            # print("PROP:windows")
            from JumpScale9Lib.sal.windows.Windows import WindowsSystem as WindowsSystem
            self._windows = WindowsSystem()
        return self._windows

    @property
    def ufw(self):
        if self._ufw is None:
            # print("PROP:ufw")
            from JumpScale9Lib.sal.ufw.UFWManager import UFWManager as UFWManager
            self._ufw = UFWManager()
        return self._ufw

    @property
    def bind(self):
        if self._bind is None:
            # print("PROP:bind")
            from JumpScale9Lib.sal.bind.BindDNS import BindDNS as BindDNS
            self._bind = BindDNS()
        return self._bind

    @property
    def ubuntu(self):
        if self._ubuntu is None:
            # print("PROP:ubuntu")
            from JumpScale9Lib.sal.ubuntu.Ubuntu import Ubuntu as Ubuntu
            self._ubuntu = Ubuntu()
        return self._ubuntu

    @property
    def openvswitch(self):
        if self._openvswitch is None:
            # print("PROP:openvswitch")
            from JumpScale9Lib.sal.openvswitch.NetConfigFactory import NetConfigFactory as NetConfigFactory
            self._openvswitch = NetConfigFactory()
        return self._openvswitch

    @property
    def dnsmasq(self):
        if self._dnsmasq is None:
            # print("PROP:dnsmasq")
            from JumpScale9Lib.sal.dnsmasq.Dnsmasq import DNSMasq as DNSMasq
            self._dnsmasq = DNSMasq()
        return self._dnsmasq

    @property
    def ciscoswitch(self):
        if self._ciscoswitch is None:
            # print("PROP:ciscoswitch")
            from JumpScale9Lib.sal.cisco_ios.CiscoSwitchManager import CiscoSwitchManager as CiscoSwitchManager
            self._ciscoswitch = CiscoSwitchManager()
        return self._ciscoswitch


if not hasattr(j.sal,"nettools"):
    j.sal._nettools = None
    j.sal.__class__.nettools = sal.nettools
if not hasattr(j.sal,"rsync"):
    j.sal._rsync = None
    j.sal.__class__.rsync = sal.rsync
if not hasattr(j.sal,"processmanager"):
    j.sal._processmanager = None
    j.sal.__class__.processmanager = sal.processmanager
if not hasattr(j.sal,"process"):
    j.sal._process = None
    j.sal.__class__.process = sal.process
if not hasattr(j.sal,"fswalker"):
    j.sal._fswalker = None
    j.sal.__class__.fswalker = sal.fswalker
if not hasattr(j.sal,"fs"):
    j.sal._fs = None
    j.sal.__class__.fs = sal.fs
if not hasattr(j.sal,"docker"):
    j.sal._docker = None
    j.sal.__class__.docker = sal.docker
if not hasattr(j.sal,"qemu_img"):
    j.sal._qemu_img = None
    j.sal.__class__.qemu_img = sal.qemu_img
if not hasattr(j.sal,"btrfs"):
    j.sal._btrfs = None
    j.sal.__class__.btrfs = sal.btrfs
if not hasattr(j.sal,"flist"):
    j.sal._flist = None
    j.sal.__class__.flist = sal.flist
if not hasattr(j.sal,"ssl"):
    j.sal._ssl = None
    j.sal.__class__.ssl = sal.ssl
if not hasattr(j.sal,"routeros"):
    j.sal._routeros = None
    j.sal.__class__.routeros = sal.routeros
if not hasattr(j.sal,"disklayout"):
    j.sal._disklayout = None
    j.sal.__class__.disklayout = sal.disklayout
if not hasattr(j.sal,"nic"):
    j.sal._nic = None
    j.sal.__class__.nic = sal.nic
if not hasattr(j.sal,"zeronetconfig"):
    j.sal._zeronetconfig = None
    j.sal.__class__.zeronetconfig = sal.zeronetconfig
if not hasattr(j.sal,"nfs"):
    j.sal._nfs = None
    j.sal.__class__.nfs = sal.nfs
if not hasattr(j.sal,"sshd"):
    j.sal._sshd = None
    j.sal.__class__.sshd = sal.sshd
if not hasattr(j.sal,"hostsfile"):
    j.sal._hostsfile = None
    j.sal.__class__.hostsfile = sal.hostsfile
if not hasattr(j.sal,"diskmanager"):
    j.sal._diskmanager = None
    j.sal.__class__.diskmanager = sal.diskmanager
if not hasattr(j.sal,"aysfs"):
    j.sal._aysfs = None
    j.sal.__class__.aysfs = sal.aysfs
if not hasattr(j.sal,"unix"):
    j.sal._unix = None
    j.sal.__class__.unix = sal.unix
if not hasattr(j.sal,"samba"):
    j.sal._samba = None
    j.sal.__class__.samba = sal.samba
if not hasattr(j.sal,"nginx"):
    j.sal._nginx = None
    j.sal.__class__.nginx = sal.nginx
if not hasattr(j.sal,"netconfig"):
    j.sal._netconfig = None
    j.sal.__class__.netconfig = sal.netconfig
if not hasattr(j.sal,"kvm"):
    j.sal._kvm = None
    j.sal.__class__.kvm = sal.kvm
if not hasattr(j.sal,"ssl_signing"):
    j.sal._ssl_signing = None
    j.sal.__class__.ssl_signing = sal.ssl_signing
if not hasattr(j.sal,"windows"):
    j.sal._windows = None
    j.sal.__class__.windows = sal.windows
if not hasattr(j.sal,"ufw"):
    j.sal._ufw = None
    j.sal.__class__.ufw = sal.ufw
if not hasattr(j.sal,"bind"):
    j.sal._bind = None
    j.sal.__class__.bind = sal.bind
if not hasattr(j.sal,"ubuntu"):
    j.sal._ubuntu = None
    j.sal.__class__.ubuntu = sal.ubuntu
if not hasattr(j.sal,"openvswitch"):
    j.sal._openvswitch = None
    j.sal.__class__.openvswitch = sal.openvswitch
if not hasattr(j.sal,"dnsmasq"):
    j.sal._dnsmasq = None
    j.sal.__class__.dnsmasq = sal.dnsmasq
if not hasattr(j.sal,"ciscoswitch"):
    j.sal._ciscoswitch = None
    j.sal.__class__.ciscoswitch = sal.ciscoswitch


 

class core:

    def __init__(self):
        self._dirs = None
        self._platformtype = None
        self._application = None
        self._events = None
        self._errorhandler = None
        self._logger = None

    @property
    def dirs(self):
        if self._dirs is None:
            # print("PROP:dirs")
            from JumpScale9.core.Dirs import Dirs as Dirs
            self._dirs = Dirs()
        return self._dirs

    @property
    def platformtype(self):
        if self._platformtype is None:
            # print("PROP:platformtype")
            from JumpScale9.core.PlatformTypes import PlatformTypes as PlatformTypes
            self._platformtype = PlatformTypes()
        return self._platformtype

    @property
    def application(self):
        if self._application is None:
            # print("PROP:application")
            from JumpScale9.core.Application import Application as Application
            self._application = Application()
        return self._application

    @property
    def events(self):
        if self._events is None:
            # print("PROP:events")
            from JumpScale9.errorhandling.EventHandler import EventHandler as EventHandler
            self._events = EventHandler()
        return self._events

    @property
    def errorhandler(self):
        if self._errorhandler is None:
            # print("PROP:errorhandler")
            from JumpScale9.errorhandling.ErrorHandler import ErrorHandler as ErrorHandler
            self._errorhandler = ErrorHandler()
        return self._errorhandler

    @property
    def logger(self):
        if self._logger is None:
            # print("PROP:logger")
            from JumpScale9.logging.LoggerFactory import LoggerFactory as LoggerFactory
            self._logger = LoggerFactory()
        return self._logger


if not hasattr(j.core,"dirs"):
    j.core._dirs = None
    j.core.__class__.dirs = core.dirs
if not hasattr(j.core,"platformtype"):
    j.core._platformtype = None
    j.core.__class__.platformtype = core.platformtype
if not hasattr(j.core,"application"):
    j.core._application = None
    j.core.__class__.application = core.application
if not hasattr(j.core,"events"):
    j.core._events = None
    j.core.__class__.events = core.events
if not hasattr(j.core,"errorhandler"):
    j.core._errorhandler = None
    j.core.__class__.errorhandler = core.errorhandler
if not hasattr(j.core,"logger"):
    j.core._logger = None
    j.core.__class__.logger = core.logger


 

class data:

    def __init__(self):
        self._types = None
        self._cache = None
        self._treemanager = None
        self._hash = None
        self._state = None
        self._regex = None
        self._tags = None
        self._blockchain = None
        self._serializer = None
        self._nacl = None
        self._text = None
        self._idgenerator = None
        self._encryption = None
        self._cachelru = None
        self._worksheets = None
        self._nltk = None
        self._markdown = None
        self._capnp = None
        self._params = None
        self._indexfile = None
        self._indexdb = None
        self._schema = None
        self._capnp3 = None

    @property
    def types(self):
        if self._types is None:
            # print("PROP:types")
            from JumpScale9.data.types.Types import Types as Types
            self._types = Types()
        return self._types

    @property
    def cache(self):
        if self._cache is None:
            # print("PROP:cache")
            from JumpScale9.data.cache.Cache import Cache as Cache
            self._cache = Cache()
        return self._cache

    @property
    def treemanager(self):
        if self._treemanager is None:
            # print("PROP:treemanager")
            from JumpScale9.data.treemanager.Treemanager import TreemanagerFactory as TreemanagerFactory
            self._treemanager = TreemanagerFactory()
        return self._treemanager

    @property
    def hash(self):
        if self._hash is None:
            # print("PROP:hash")
            from JumpScale9.data.hash.HashTool import HashTool as HashTool
            self._hash = HashTool()
        return self._hash

    @property
    def state(self):
        if self._state is None:
            # print("PROP:state")
            from JumpScale9.data.state.StateFactory import StateFactory as StateFactory
            self._state = StateFactory()
        return self._state

    @property
    def regex(self):
        if self._regex is None:
            # print("PROP:regex")
            from JumpScale9.data.regex.RegexTools import RegexTools as RegexTools
            self._regex = RegexTools()
        return self._regex

    @property
    def tags(self):
        if self._tags is None:
            # print("PROP:tags")
            from JumpScale9.data.tags.TagsFactory import TagsFactory as TagsFactory
            self._tags = TagsFactory()
        return self._tags

    @property
    def blockchain(self):
        if self._blockchain is None:
            # print("PROP:blockchain")
            from JumpScale9.data.blockchain.BlockchainFactory import BlockchainFactory as BlockchainFactory
            self._blockchain = BlockchainFactory()
        return self._blockchain

    @property
    def serializer(self):
        if self._serializer is None:
            # print("PROP:serializer")
            from JumpScale9.data.serializers.SerializersFactory import SerializersFactory as SerializersFactory
            self._serializer = SerializersFactory()
        return self._serializer

    @property
    def nacl(self):
        if self._nacl is None:
            # print("PROP:nacl")
            from JumpScale9.data.nacl.NACLClientFactory import NACLClientFactory as NACLClientFactory
            self._nacl = NACLClientFactory()
        return self._nacl

    @property
    def text(self):
        if self._text is None:
            # print("PROP:text")
            from JumpScale9.data.text.Text import Text as Text
            self._text = Text()
        return self._text

    @property
    def idgenerator(self):
        if self._idgenerator is None:
            # print("PROP:idgenerator")
            from JumpScale9.data.idgenerator.IDGenerator import IDGenerator as IDGenerator
            self._idgenerator = IDGenerator()
        return self._idgenerator

    @property
    def encryption(self):
        if self._encryption is None:
            # print("PROP:encryption")
            from JumpScale9Lib.data.encryption.EncryptionFactory import EncryptionFactory as EncryptionFactory
            self._encryption = EncryptionFactory()
        return self._encryption

    @property
    def cachelru(self):
        if self._cachelru is None:
            # print("PROP:cachelru")
            from JumpScale9Lib.data.cachelru.LRUCacheFactory import LRUCacheFactory as LRUCacheFactory
            self._cachelru = LRUCacheFactory()
        return self._cachelru

    @property
    def worksheets(self):
        if self._worksheets is None:
            # print("PROP:worksheets")
            from JumpScale9Lib.data.worksheets.Sheets import Sheets as Sheets
            self._worksheets = Sheets()
        return self._worksheets

    @property
    def nltk(self):
        if self._nltk is None:
            # print("PROP:nltk")
            from JumpScale9Lib.data.nltk.NLTK import NLTKFactory as NLTKFactory
            self._nltk = NLTKFactory()
        return self._nltk

    @property
    def markdown(self):
        if self._markdown is None:
            # print("PROP:markdown")
            from JumpScale9Lib.data.markdown.MarkdownFactory import MarkdownFactory as MarkdownFactory
            self._markdown = MarkdownFactory()
        return self._markdown

    @property
    def capnp(self):
        if self._capnp is None:
            # print("PROP:capnp")
            from JumpScale9Lib.data.capnp.Capnp import Capnp as Capnp
            self._capnp = Capnp()
        return self._capnp

    @property
    def params(self):
        if self._params is None:
            # print("PROP:params")
            from JumpScale9Lib.data.params.Params import ParamsFactory as ParamsFactory
            self._params = ParamsFactory()
        return self._params

    @property
    def indexfile(self):
        if self._indexfile is None:
            # print("PROP:indexfile")
            from JumpScale9RecordChain.data.indexFile.IndexFiles import IndexDB as IndexDB
            self._indexfile = IndexDB()
        return self._indexfile

    @property
    def indexdb(self):
        if self._indexdb is None:
            # print("PROP:indexdb")
            from JumpScale9RecordChain.data.IndexDB.IndexDB import IndexDB as IndexDB
            self._indexdb = IndexDB()
        return self._indexdb

    @property
    def schema(self):
        if self._schema is None:
            # print("PROP:schema")
            from JumpScale9RecordChain.data.schema.SchemaFactory import SchemaFactory as SchemaFactory
            self._schema = SchemaFactory()
        return self._schema

    @property
    def capnp3(self):
        if self._capnp3 is None:
            # print("PROP:capnp3")
            from JumpScale9RecordChain.data.capnp3.Capnp import Capnp as Capnp
            self._capnp3 = Capnp()
        return self._capnp3


if not hasattr(j.data,"types"):
    j.data._types = None
    j.data.__class__.types = data.types
if not hasattr(j.data,"cache"):
    j.data._cache = None
    j.data.__class__.cache = data.cache
if not hasattr(j.data,"treemanager"):
    j.data._treemanager = None
    j.data.__class__.treemanager = data.treemanager
if not hasattr(j.data,"hash"):
    j.data._hash = None
    j.data.__class__.hash = data.hash
if not hasattr(j.data,"state"):
    j.data._state = None
    j.data.__class__.state = data.state
if not hasattr(j.data,"regex"):
    j.data._regex = None
    j.data.__class__.regex = data.regex
if not hasattr(j.data,"tags"):
    j.data._tags = None
    j.data.__class__.tags = data.tags
if not hasattr(j.data,"blockchain"):
    j.data._blockchain = None
    j.data.__class__.blockchain = data.blockchain
if not hasattr(j.data,"serializer"):
    j.data._serializer = None
    j.data.__class__.serializer = data.serializer
if not hasattr(j.data,"nacl"):
    j.data._nacl = None
    j.data.__class__.nacl = data.nacl
if not hasattr(j.data,"text"):
    j.data._text = None
    j.data.__class__.text = data.text
if not hasattr(j.data,"idgenerator"):
    j.data._idgenerator = None
    j.data.__class__.idgenerator = data.idgenerator
if not hasattr(j.data,"encryption"):
    j.data._encryption = None
    j.data.__class__.encryption = data.encryption
if not hasattr(j.data,"cachelru"):
    j.data._cachelru = None
    j.data.__class__.cachelru = data.cachelru
if not hasattr(j.data,"worksheets"):
    j.data._worksheets = None
    j.data.__class__.worksheets = data.worksheets
if not hasattr(j.data,"nltk"):
    j.data._nltk = None
    j.data.__class__.nltk = data.nltk
if not hasattr(j.data,"markdown"):
    j.data._markdown = None
    j.data.__class__.markdown = data.markdown
if not hasattr(j.data,"capnp"):
    j.data._capnp = None
    j.data.__class__.capnp = data.capnp
if not hasattr(j.data,"params"):
    j.data._params = None
    j.data.__class__.params = data.params
if not hasattr(j.data,"indexfile"):
    j.data._indexfile = None
    j.data.__class__.indexfile = data.indexfile
if not hasattr(j.data,"indexdb"):
    j.data._indexdb = None
    j.data.__class__.indexdb = data.indexdb
if not hasattr(j.data,"schema"):
    j.data._schema = None
    j.data.__class__.schema = data.schema
if not hasattr(j.data,"capnp3"):
    j.data._capnp3 = None
    j.data.__class__.capnp3 = data.capnp3


 

class data_units:

    def __init__(self):
        self._sizes = None

    @property
    def sizes(self):
        if self._sizes is None:
            # print("PROP:sizes")
            from JumpScale9Lib.data.units.Units import Sizes as Sizes
            self._sizes = Sizes()
        return self._sizes


if not hasattr(j.data_units,"sizes"):
    j.data_units._sizes = None
    j.data_units.__class__.sizes = data_units.sizes


 

class servers:

    def __init__(self):
        self._gedisexample = None
        self._gedis = None
        self._raftserver = None
        self._dns = None
        self._zdb = None
        self._uidserver = None

    @property
    def gedisexample(self):
        if self._gedisexample is None:
            # print("PROP:gedisexample")
            from JumpScale9RecordChain.servers.gedis_example.GedisExampleServerFactory import GedisExampleServerFactory as GedisExampleServerFactory
            self._gedisexample = GedisExampleServerFactory()
        return self._gedisexample

    @property
    def gedis(self):
        if self._gedis is None:
            # print("PROP:gedis")
            from JumpScale9RecordChain.servers.gedis.GedisFactory import GedisFactory as GedisFactory
            self._gedis = GedisFactory()
        return self._gedis

    @property
    def raftserver(self):
        if self._raftserver is None:
            # print("PROP:raftserver")
            from JumpScale9RecordChain.servers.raft.RaftServerFactory import RaftServerFactory as RaftServerFactory
            self._raftserver = RaftServerFactory()
        return self._raftserver

    @property
    def dns(self):
        if self._dns is None:
            # print("PROP:dns")
            from JumpScale9RecordChain.servers.dns.DNSServerFactory import DNSServerFactory as DNSServerFactory
            self._dns = DNSServerFactory()
        return self._dns

    @property
    def zdb(self):
        if self._zdb is None:
            # print("PROP:zdb")
            from JumpScale9RecordChain.servers.zdb.ZDBServers import ZDBServers as ZDBServers
            self._zdb = ZDBServers()
        return self._zdb

    @property
    def uidserver(self):
        if self._uidserver is None:
            # print("PROP:uidserver")
            from JumpScale9RecordChain.servers.uid_server.UIDServerFactory import UIDServerFactory as UIDServerFactory
            self._uidserver = UIDServerFactory()
        return self._uidserver


if not hasattr(j.servers,"gedisexample"):
    j.servers._gedisexample = None
    j.servers.__class__.gedisexample = servers.gedisexample
if not hasattr(j.servers,"gedis"):
    j.servers._gedis = None
    j.servers.__class__.gedis = servers.gedis
if not hasattr(j.servers,"raftserver"):
    j.servers._raftserver = None
    j.servers.__class__.raftserver = servers.raftserver
if not hasattr(j.servers,"dns"):
    j.servers._dns = None
    j.servers.__class__.dns = servers.dns
if not hasattr(j.servers,"zdb"):
    j.servers._zdb = None
    j.servers.__class__.zdb = servers.zdb
if not hasattr(j.servers,"uidserver"):
    j.servers._uidserver = None
    j.servers.__class__.uidserver = servers.uidserver


 

