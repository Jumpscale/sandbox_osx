from zeroos.zerohub import Client as ZHubClient
from js9 import j

JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
token_ = ""
username = ""
"""


class ZeroHubClient(JSConfigClient):
    """
    Provide an easy way to communicate and do some actions on the ZeroHub
    """

    def __init__(self, instance, data={}, parent=None):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE)
        self.token = self.config.data['token_']
        self.username = self.config.data['username']
        self.client = ZHubClient("https://staging.hub.gig.tech/api")
        self.api = self.client.api

    def authentificate(self):
        """
        This is fastest way to authentifcate yourself.

        By providing a valid token (jwt) to this method, you have nothing more
        to do. A valid jwt can be extracted from your brower cookies or generated
        using some itsyou.online endpoint

        Please use j.clients.itsyouonline to generare a token, any valid token with
        a username set is valid. To allows multi-users (eg: for organization upload),
        please add a scope `user:memberof:[organization]` to your token.

        If you have scope for another username than your, you can specify
        which username you want to use via the 'username' argument.
        """
        self.api.set_token(self.token)

        if self.username:
            self.api.set_user(self.username)

        return True

    def repositories(self):
        """
        Returns available repositories (users) in a list
        """
        return self.api.repositories.repositories_get().json()

    def list(self, username=None):
        """
        Returns a list of available flists files
        If username is set to None (by default), all availables flist will be listed
        If you provide a username, only flists on this repository will be listed
        """
        if not username:
            return self.api.flist.flist_get().json()

        return self.api.flist.flist_byUsername_get(username).json()

    def get(self, username, flist):
        """
        Get information about a specific flist
        Theses informations contains files, directories, symlinks, etc. in the archive
        """
        return self.api.flist.flist_byUsernameflist_get(username, flist).json()

    def upload(self, filename):
        """
        Upload an archive (.tar.gz) to the hub, this archive will be converted to an flist
        automatically after being uploaded.

        This method require authentification (see authentificate method)
        """
        return self.api.flist.flist_meupload_post({'file': open(filename, 'rb')}, content_type='multipart/form-data')

    def rename(self, source, destination):
        """
        Rename one of your flist from 'source' to 'destination'
        You can only change the name of the flist, not the owner (repository)

        This method require authentification (see authentificate method)
        """
        return self.api.flist.flist_meflistrenametarget_get(source, destination).json()

    def symlink(self, source, linkname):
        """
        Create a link (symlink) called 'linkname' pointing to 'source'

        This is useful when you want to upload multiple version of a flist and
        pointing to the last version, without overwriting the flist

        This method require authentification (see authentificate method)
        """
        return self.api.flist.flist_meflistlinklinkname_get(source, linkname).json()

    def delete(self, filename):
        """
        Delete one of your flist. Warning, this action cannot be reverted.

        This method require authentification (see authentificate method)
        """
        return self.api.flist.flist_meflist_delete(filename).json()

    def sandbox_upload(self, path):
        """
        use sandboxer in jumpscale, to create clean destination with all libs inside
        upload this to hub in most performant & efficient manner

        all what people need to do this action should be called from this method

        """
        pass
