from requests.exceptions import HTTPError
from js9 import j

JSBASE = j.application.jsbase_get_class()


def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp


class ActorTemplates(JSBASE):
    def __init__(self, repository=None, client=None):
        JSBASE.__init__(self)
        self._repository = repository
        if repository:
            self._ayscl = repository._ayscl
        if client:
            self._ayscl = client._ayscl

    def list(self, role=None, name=None):
        """
        List all actor templates.

        Args:
            role: in order to only return the templates with a specific rol, e.g. "node" will return all node templates
            name: name of the actor templates to return, e.g. "node.ovc" will only return the node templates for OpenvCloud

        Returns: list of actor templates
        """
        if self._repository:
            return self._listLocalTemplates(role, name)
        else:
            return self._listGlobalTemplates(role, name)

    def _listLocalTemplates(self, role=None, name=None):
        """
        List all local (local to the repository) actor templates;

        Returns: list of actor templates
        """

        try:
            resp = self._ayscl.listTemplates(self._repository.model['name'])
        except Exception as e:
            return _extract_error(e)

        ays_templates = resp.json()
        templates = list()

        for template in sorted(ays_templates, key=lambda template: template['name']):
            if role and template['role'] != role:
                continue
            if name and template['name'] != name:
                continue
            try:
                ays_template = self._ayscl.getTemplate(template['name'], self._repository.model['name'])
            except Exception as e:
                return _extract_error(e)
            templates.append(ActorTemplate(ays_template.json()))
        return templates

    def _listGlobalTemplates(self, role=None, name=None):
        """
        Returns a list of all (global) AYS templates.
        """
        try:
            resp = self._ayscl.listAYSTemplates()
        except Exception as e:
            return _extract_error(e)

        ays_templates = resp.json()
        templates = list()

        for template in sorted(ays_templates, key=lambda template: template['name']):
            if role and template['role'] != role:
                continue
            if name and template['name'] != name:
                continue
            try:
                ays_template = self._ayscl.getAYSTemplate(template['name'])
            except Exception as e:
                return _extract_error(e)
            templates.append(ActorTemplate(ays_template.json()))
        return templates

    def addTemplates(self, repo_url, branch):
        """
        Adds AYS global templates from a give Git repository. Not available yet for adding local templates.

        Args:
            repo_url: URL of the Git repository with the templates to import, e.g. "https://github.com/openvcloud/ays_templates"
            branch: branch name in the Git repository, e.g. "master"

        Returns: HTTP response object.

        Raises: HTTPError error message.
        """

        if self._repository is None:
            data = {'url': repo_url,'branch': branch}
            try:
                resp = self._ayscl.addTemplateRepo(data)
            except Exception as e:
                return _extract_error(e)
            return resp

    def get(self, name):
        """
        Get an actor template by name.

        Args:
            name: name of the actor template

        Returns: actor template instance

        Raises: KeyError when no service match the specified arguments
        """
        for template in self.list():
            if template.model['name'] == name:
                return template
        raise KeyError("Could not find template with name {}".format(role, name))

class ActorTemplate(JSBASE):
    def __init__(self, model):
        JSBASE.__init__(self)
        self.model = model

    def __repr__(self):
        return "%s" % (self.model["name"])

    __str__ = __repr__
