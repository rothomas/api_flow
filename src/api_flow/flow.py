import os
from functools import reduce
from api_flow.config import Config
from api_flow.context import Context
from api_flow.profiles import Profiles
from api_flow.step import Step


class Flow(Context):
    """
    Reads in a YAML file containing configuration for a flow and its associated
    steps and allows execution of the flow.  Flows are expressed as a dict
    where keys are a unique step identifier and the value is a step
    configuration dict using the structure described in the Step class.
    As each step is executed, it becomes available to subsequent steps,
    using the step identifier as a property of the inherited context.
    """

    def __init__(self, flow_name, profile=None, profiles=None, parent=None, **kwargs):
        """
        Flow constructor.  Loads a named flow as YAML from the
        *Config.flows_path* directory.

        :argument flow_name: the base filename of a flow configuration file
                            that exists (with .yaml extension) in directory
                            identified by "Config.flows_path".
        :type flow_name: str
        :argument profile: An optional convenience argument for a singular
                          profile equivalent to "profiles=['profile_name']".
        :type profile: str | None
        :argument profiles: An optional list of strings that specify
                           YAML profile files to load from. The '.yaml' file
                           extension should be omitted, but subdirectories of
                           the flow path are supported for organization.
                           If both "profiles" and "profile" are specified, the
                           "profile" value is appended to the end of the
                           "profiles" list (so it will be the lowest
                           precedence).
        :type profiles: list[str] | None
        :argument parent: optional context from which this flow inherits values
        :type parent: Context
        :argument kwargs: additional arguments stored as context vars
        :type kwargs: dict[any]
        """
        super().__init__(parent=parent, **kwargs)
        self.flow_name = flow_name
        if profile or profiles:
            self.merge(Profiles(profile=profile, profiles=profiles))
        self.flow_definition = self.from_yaml(os.path.join(
            Config.flow_path,
            f"{self.flow_name}.yaml"
        ))
        self.flow_description = self.flow_definition.get('description', self.flow_name)
        self.flow_dependencies = self._get_flow_dependencies()
        self.flow_steps = self.flow_definition.get('steps', {})
        self.flow_store = self._get_flow_store()
        self.flow_dependencies_succeeded = None
        self.flow_steps_succeeded = None
        self.succeeded = False
        setattr(self.flow_store, flow_name, self)
        if isinstance(parent, Flow):
            setattr(parent, flow_name, self)

    def _get_flow_dependencies(self):
        depends_on = self.flow_definition.get('depends_on', [])
        if not isinstance(depends_on, list):
            depends_on = [depends_on]
        return depends_on

    def _get_flow_store(self):
        if not hasattr(self, '_flow_store'):
            self.set_global('_flow_store', Context())
        return self._flow_store

    def _execute_dependencies(self):
        if self.flow_dependencies_succeeded is None:
            if self.flow_dependencies:
                print(f'Executing prerequisites for {self.flow_description}')
                self.flow_dependencies_succeeded = reduce(
                    lambda r, dependency: r and dependency.execute(),
                    [Flow(dependency, parent=self) for dependency in self.flow_dependencies],
                    True
                )
                if self.flow_dependencies_succeeded:
                    self.flow_store.current_flow = self
            else:
                self.flow_dependencies_succeeded = True
        return self.flow_dependencies_succeeded

    def _execute_steps(self):
        if self.flow_steps_succeeded is None:
            if self.flow_steps.keys():
                print(f'Executing steps for {self.flow_description}')
                self.flow_steps_succeeded = reduce(
                    lambda r, step: r and step.execute(),
                    [Step(step[0], step[1], parent=self) for step in self.flow_steps.items()],
                    True
                )
            else:
                self.flow_steps_succeeded = True
        return self.flow_steps_succeeded

    def execute(self):
        print(f'Executing flow {self.flow_description}')
        self.flow_store.current_flow = self
        self.succeeded = self._execute_dependencies() and self._execute_steps()
        if self.succeeded:
            self.flow_store.previous_flow = self
            self.flow_store.current_flow = None
        else:
            flow_name = self.flow_store.current_flow.flow_name
            step_name = self.flow_store.current_step.step_name
            print(f"Flow \"{flow_name}\" failed at step \"{step_name}\".")
        return self.succeeded
