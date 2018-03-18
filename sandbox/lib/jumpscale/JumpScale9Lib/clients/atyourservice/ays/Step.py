from .Job import Jobs
from js9 import j

JSBASE = j.application.jsbase_get_class()


class Steps(JSBASE):
    def __init__(self, run):
        JSBASE.__init__(self)
        self._run = run

    def list(self):
        """
        List all steps.

        Returns: list of steps
        """
        steps = list()

        for step in self._run.model['steps']:
            steps.append(Step(self._run, step))
        return steps

    def get(self, number):
        """
        Get a step by its number.

        Args:
            number: number of the step

        Raises: ValueError if no step with given number could be found

        Returns: step with given number
        """
        for step in self.list():
            if step.model['number'] == number:
                return step
        raise ValueError("Could not find step with number {}".format(number))

class Step(JSBASE):
    def __init__(self, run, model):
        JSBASE.__init__(self)
        self._run = run
        self.model = model
        self.jobs = Jobs(step=self)

    def __repr__(self):
        return "step number %s (%s): %s jobs" % (self.model["number"], self.model["state"], len(self.model['jobs']))

    __str__ = __repr__
