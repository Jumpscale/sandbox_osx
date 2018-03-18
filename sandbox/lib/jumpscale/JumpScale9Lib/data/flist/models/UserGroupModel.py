
from js9 import j

from JumpScale9Lib.data.capnp.ModelBase import ModelBase


class UserGroupModel(ModelBase):
    """
    usergroup model, needs unique key as uint16, all to get as dense as possible solution in mem & on disk
    """

    @property
    def key(self):
        if self._key == "":
            from IPython import embed
            self.logger.debug("DEBUG NOW generate key UserGroup")
            embed()
            raise RuntimeError("stop debug here")
        return self._key
