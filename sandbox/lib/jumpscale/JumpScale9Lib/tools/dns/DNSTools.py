from __future__ import print_function
from js9 import j


try:
    import dns
    import dns.message
    import dns.rdataclass
    import dns.rdatatype
    import dns.query
    import dns.resolver
except Exception as e:
    print("WARNING install dnspython: 'pip3 install dnspython'")

JSBASE = j.application.jsbase_get_class()


class DNSTools(JSBASE):
    """
    to install:
    pip3 install dnspython
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.dnstools"
        JSBASE.__init__(self)
        self._default = None

    def get(self, nameservers=["8.26.56.26", "8.20.247.20"]):  #https://www.computerworld.com/article/2872700/endpoint-security/6-dns-services-protect-against-malware-and-other-unwanted-content.html?page=3
        if "localhost" in nameservers:
            nameservers.pop(nameservers.index("localhost"))
            nameservers.append("127.0.0.1")
        return DNSClient(nameservers=nameservers)

    @property
    def default(self):
        if self._default == None:
            self._default = self.get()

        return self._default

    def test(self,start=False):
        """
        js9 'j.tools.dnstools.test()'
        """            

        answer=self.default.resolver.query("www.yelp.com", 'A')



class DNSClient(JSBASE):

    def __init__(self, nameservers):
        JSBASE.__init__(self)
        self.nameservers=nameservers
        self.resolver=dns.resolver.Resolver(configure = False)
        self.resolver.nameservers=self.nameservers


    def nameservers_get(self, domain = "threefoldtoken.org"):

        answer=self.resolver.query(domain, 'NS')

        res=[]
        for rr in answer:
            res.append(rr.target.to_text())
        return res

    def namerecords_get(self, dnsurl = "www.threefoldtoken.org"):
        """
        return ip addr for a full name
        """

        answer=self.resolver.query(dnsurl, 'A')

        res=[]
        for rr in answer:
            res.append(rr.address)
        return res
