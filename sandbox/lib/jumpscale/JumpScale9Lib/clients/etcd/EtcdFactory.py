import etcd
from js9 import j

JSBASE = j.application.jsbase_get_class()


class EtcdFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.clients.etcd"
        JSBASE.__init__(self)
        self.__imports__ = "python-etcd"

    def get(self, **kwargs):
        """
        Initialize the client.
        Args:
            host (mixed):
                           If a string, IP to connect to.
                           If a tuple ((host, port), (host, port), ...)
            port (int):  Port used to connect to etcd.
            srv_domain (str): Domain to search the SRV record for cluster autodiscovery.
            version_prefix (str): Url or version prefix in etcd url (default=/v2).
            read_timeout (int):  max seconds to wait for a read.
            allow_redirect (bool): allow the client to connect to other nodes.
            protocol (str):  Protocol used to connect to etcd.
            cert (mixed):   If a string, the whole ssl client certificate;
                            if a tuple, the cert and key file names.
            ca_cert (str): The ca certificate. If pressent it will enable
                           validation.
            username (str): username for etcd authentication.
            password (str): password for etcd authentication.
            allow_reconnect (bool): allow the client to reconnect to another
                                    etcd server in the cluster in the case the
                                    default one does not respond.
            use_proxies (bool): we are using a list of proxies to which we connect,
                                 and don't want to connect to the original etcd cluster.
            expected_cluster_id (str): If a string, recorded as the expected
                                       UUID of the cluster (rather than
                                       learning it from the first request),
                                       reads will raise EtcdClusterIdChanged
                                       if they receive a response with a
                                       different cluster ID.
            per_host_pool_size (int): specifies maximum number of connections to pool
                                      by host. By default this will use up to 10
                                      connections.
        """
        return etcd.Client(**kwargs)
