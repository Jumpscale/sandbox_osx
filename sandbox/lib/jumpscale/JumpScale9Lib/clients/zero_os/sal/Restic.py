from js9 import j

from . import templates


logger = j.logger.get(__name__)


class Restic:

    def __init__(self, container, repo):
        """
        :param container: sal of the container running restic
        :param repo: repo to use
        """
        self.container = container
        start = 's3:http'
        if not repo.startswith(start):
            raise ValueError('Repo expected to start with %s' % start)
        self.repo = repo
        self._password_file = '/bin/repo_password'

    def init_repo(self, password):
        """
        Initialize a restic repo and create the password file
        """
        logger.info('Initializing repo %s' % self.repo)
        self.container.upload_content(self._password_file, password)

        cmd = '/bin/restic init -r {repo} -p {password}'.format(repo=self.repo, password=self._password_file)
        return self.container.client.system(cmd).get()

    def backup(self, dir):
        """
        Backup a directory to the restic repo
        :param dir: the directory to backup
        """
        logger.info('Backing up dir %s to repo %s' % (dir, self.repo))
        cmd = '/bin/restic backup {dir} -r {repo} -p {password}'.format(
            dir=dir, repo=self.repo, password=self._password_file)
        return self.container.client.system(cmd).get()

    def restore(self, dir, snapshot='latest'):
        """
        Restore a snapshot
        :param dir: directory to restore to
        :param snapshot: snapshot name
        """
        logger.info('Restoring snapshot %s to dir %s from repo %s' % (snapshot, dir, self.repo))
        cmd = '/bin/restic restore {snapshot} -t {dir} -r {repo} -p {password}'.format(
            snapshot=snapshot, dir=dir, repo=self.repo, password=self._password_file)
        return self.container.client.system(cmd).get()
