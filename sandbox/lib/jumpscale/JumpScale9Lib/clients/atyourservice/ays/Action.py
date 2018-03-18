from js9 import j

JSBASE = j.application.jsbase_get_class()


class Actions(JSBASE):
    def __init__(self, service):
        JSBASE.__init__(self)
        self._service = service
        self._repository = service._repository
        self._ayscl = service._repository._ayscl

    def list(self, state=None, recurring=None):
        """
        List all actions.

        Args:
            state: allowing you to filter on state

        Returns:
            list of actions
        """
        actions = list()

        if self._service.model['actions']:
            for action in self._service.model['actions']:
                if state and action['state'] != state:
                    continue
                if recurring and action['recurring'] is None:
                   continue
                actions.append(Action(self._service, action))

        return actions

    def get(self, name):
        """
        Get the action with a given name.

        Args:
            name: name of the action.

        Returns:
            action instance

        Raises:
            KeyError is an action with given name was not found.
        """
        for action in self.list():
            if action.model['name'] == name:
                return action
        raise KeyError("Could not find action with name {}".format(name))


class Action(JSBASE):
    def __init__(self, service, model):
        JSBASE.__init__(self)
        self._service = service
        self._repository = service._repository
        self._ayscl = service._repository._ayscl
        self.model = model

    def __repr__(self):
        return "action: %s" % (self.model["name"])

    __str__ = __repr__