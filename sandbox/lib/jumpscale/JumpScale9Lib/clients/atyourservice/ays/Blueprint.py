import json
import os
from js9 import j

JSBASE = j.application.jsbase_get_class()


class Blueprints(JSBASE):
    def __init__(self, repository):
        JSBASE.__init__(self)
        self._repository = repository
        self._ayscl = repository._ayscl

    def list(self, archived=False):
        """
        List all blueprints.

        Args:
            archived (True/False): If true also the archived blueprints are listed (Default is False)

        Returns:
            list of blueprints
        """
        query_params={'archived': archived}
        ays_blueprints = self._ayscl.listBlueprints(self._repository.model.get('name', query_params)).json()
        blueprints = list()
        for blueprint in ays_blueprints:
            blueprints.append(Blueprint(self._repository, blueprint))
        return blueprints

    def get(self, name):
        """
        Get the blueprint with a given name.

        Args:
            name: name of the blueprint.

        Returns:
            blueprint instance

        Raises:
            KeyError if blueprint with given name was not found.
        """
        for blueprint in self.list():
            if blueprint.model['name'] == name:
                return blueprint
        raise KeyError("Could not find blueprint with name {}".format(name))

    def create(self, name, blueprint):
        """
        Create a blueprint.

        Args:
            name: name of the blueprint, as it will be saved to disk and referenced.
            blueprint: blueprint as a string

        Returns:
            blueprint instance
        """
        data = {
            'name': name,
            'content': blueprint
        }

        json_str = json.dumps(data)

        resp = self._ayscl.createBlueprint(json_str, self._repository.model["name"],)

        return self.get(name)

    def execute(self, name=None):
        """
        Executes all blueprints, or a single blueprint specified by name.

        Args:
            name: (optional) name of a blueprint, in case only one blueprint needs to be executed

        Returns: nothing
        """

        if name is None:
            try:
                resp = self._ayscl.listBlueprints(self._repository.model["name"], query_params={'archived': False})
            except Exception as e:
                return
            blueprints = resp.json()
            names = [bp['name'] for bp in blueprints]
        else:
            names = [name]

        for name in sorted(names):
            try:
                resp = self._ayscl.executeBlueprint(data='', blueprint=name, repository=self._repository.model["name"])
            except Exception as e:
                return

class Blueprint(JSBASE):
    def __init__(self, repository, model):
        JSBASE.__init__(self)
        self._repository = repository
        self._ayscl = repository._ayscl
        self.model = model

    def execute(self):
        """
        Execute the blueprint.

        Args: none

        Returns: HTTP response object
        """
        resp = self._ayscl.executeBlueprint('', self.model['name'], self._repository.model['name'])
        return resp

    def delete(self):
        """
        Delete the blueprint.

        Args: none

        Returns: HTTP response object
        """
        resp = self._ayscl.deleteBlueprint(blueprint=self.model['name'], repository=self._repository.model['name'])
        return resp

    def get(self):
        """
        Get the actual blueprint content

        Args: none

        Returns: blueprint content
        """
        resp = self._ayscl.getBlueprint(blueprint=self.model['name'], repository=self._repository.model['name'])
        data=resp.json()
        return data['content']

    def archive(self):
        """
        Archive a blueprint

        Args: none

        Returns: HTTP response object
        """
        resp = self._ayscl.archiveBlueprint(data='', blueprint=self.model['name'], repository=self._repository.model['name'])
        return resp

    def restore(self):
        """
        Restore an archived blueprint

        Args: none

        Returns: HTTP response object
        """
        resp = self._ayscl.restoreBlueprint(data='', blueprint=self.model['name'], repository=self._repository.model['name'])
        return resp

    def __repr__(self):
        return "blueprint: %s" % (self.model["name"])

    __str__ = __repr__
