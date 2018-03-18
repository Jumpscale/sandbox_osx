from requests.exceptions import HTTPError
from .Action import Actions
from .EventHandler import EventHandlers
from js9 import j

JSBASE = j.application.jsbase_get_class()


def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp


class Services(JSBASE):
    def __init__(self, repository, relatedService=None, relationship=None):
        JSBASE.__init__(self)
        self._repository = repository
        self._ayscl = repository._ayscl
        self._relatedService=relatedService
        self._relationship=relationship

    def list(self, role=None, name=None):
        """
        List all AYS services with specific role and instance name, and/or relationship to other services

        Args:
            role: role of the service
            name: name of the service
            service: other service with which the service has relationship (default: None)
            relationship: relationship (children/consumers/producers) to given reference service (default:None)

        Returns: list of services
        """

        def AppendIfMatch(services, service, role=None, name=None):
            if role and service['role'] != role:
                return
            if name and service['name'] != name:
                return
            try:
                ays_service = self._ayscl.getServiceByName(service['name'], service['role'], self._repository.model['name'])
            except Exception as e:
                return _extract_error(e)
            services.append(Service(self._repository, ays_service.json()))

        services = list()

        if self._relationship is None:
            try:
                resp = self._ayscl.listServices(self._repository.model.get('name'))
            except Exception as e:
                return _extract_error(e)
            ays_services = resp.json()

            for service in sorted(ays_services, key=lambda service: '{role}!{name}'.format(**service)):
                AppendIfMatch(services, service, role, name)

        else:
            if self._relationship == 'children':
                if self._relatedService and self._relatedService.model['children']:
                    for child in self._relatedService.model['children']:
                        AppendIfMatch(services, child, role, name)
            if self._relationship == 'consumers':
                if self._relatedService and self._relatedService.model['consumers']:
                    for consumer in self._relatedService.model['consumers']:
                        AppendIfMatch(services, consumer, role, name)
            if self._relationship == 'producers':
                if self._relatedService and self._relatedService.model['producers']:
                    for producer in self._relatedService.model['producers']:
                        AppendIfMatch(services, producer, role, name)

        return services

    def get(self, role, name):
        """
        Get the AYS service with a specific role and instance name.

        Args:
            role: role of the service
            name: name of the service

        Returns: service instance

        Raises: KeyError when no service match the specified arguments.
        """
        for service in self.list():
            if service.model['role'] == role and service.model['name'] == name:
                return service
        raise KeyError("Could not find service with role {} and name {}".format(role, name))

    def delete(self, role, name):
        """
        Delete all services with a specific role and instance name.

        Args:
            role: role of the service
            name: name of the service

        Returns: nothing if succesful. else error from HTTP response object
        """
        try:
            for service in sorted(self.list(role, name), key=lambda service: service['role']):
                self._ayscl.deleteServiceByName(name=service['name'], role=service['role'], repository=self._repository.mode['name'])
        except Exception as e:
            return _extract_error(e)


class Service(JSBASE):
    def __init__(self, repository, model):
        JSBASE.__init__(self)
        self._repository = repository
        self._ayscl = repository._ayscl
        self.model = model
        self.actions = Actions(self)
        self.eventHandlers = EventHandlers(self)
        self.children = Services(self._repository, self, 'children')
        self.consumers = Services(self._repository, self, 'consumers')
        self.producers = Services(self._repository,self, 'producers')

    def show(self):
        return

    def state(self):
        return

    def getParent(self):
        """
        Get parent with a specified name and/or role

        Args: none

        Returns: parent, or none if no parent
        """
        if self.model['parent']:
            return Service(self._repository, self.model['parent'])
        else:
            return None

    def delete(self):
        """
        Delete a service and all its children.
        Be carefull with this action, there is undo option.

        Returns: HTTP response object
        """
        resp = self._ayscl.deleteServiceByName(name=self.model['name'], role=self.model['role'], repository=self._repository.model['name'])
        return resp

    def __repr__(self):
        return "service: %s!%s" % (self.model["role"], self.model["name"])

    __str__ = __repr__
