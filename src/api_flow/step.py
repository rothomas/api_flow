import time
from functools import reduce
from jsonpath_ng import parse
from api_flow.complex_namespace import ComplexNamespace
from api_flow.context import Context
from api_flow.request import Request
from api_flow.template import Template


# Baseline configuration for retryable requests.
# These are only applied if wait_for_success is
# provided in the step definition.
DEFAULT_ATTEMPT_COUNT = 3
DEFAULT_DELAY_SECONDS = 5
RUN_ONCE = {
    'attempt': 1,
    'delay': 0
}
RETRY = {
    'attempt': DEFAULT_ATTEMPT_COUNT,
    'delay': DEFAULT_DELAY_SECONDS
}


class Step(Context):
    """ a class representing a single API request
        After the request is executed, the following properties are available on the step object:
        - response (Response): the raw result of the requests call
        - status_code (int): the HTTP status code from the response
        - succeeded (boolean): whether the HTTP request was successful
        - mapped properties as defined by the "outputs" section of the step config.

        Substitution values are available from the parent context, which will include the base environment values and
        output from previous steps.  The previous steps can be referred to by their YAML dict key string.  As a
        shortcut, the step immediately prior to this one in the current flow is available as 'previous_step'.

        For instance, in a flow starting with "step_one" with an output "my_value", a valid substitution would be
        {? step_one.my_value ?}, but in "step_two" this could also be expressed {? previous_step.my_value ?}.
    """

    def __init__(self, step_name, step_definition, parent=None):
        """ Step constructor
            :argument step_name (str) The name string derived from the Flow yaml.  Used in output if no description.
            :argument step_definition (dict) The step structure pulled from the Flow yaml.
                      The step can contain the following fields:
                      description (str): (optional) a descriptive string used in output
                      url (str): (required) the URL for the request
                      method (str): (optional) an HTTP request method (default GET)
                      headers (dict): (optional) a dict of HTTP headers to send with the request (default above)
                      body (str): (optional) the body for requests that require one.
                                  The body can be defined in YAML, and will be rendered as JSON for the request,
                                  or can load a JSON template from the templates directory using, e.g.,
                                  template:my_template as the body value.
                      outputs (dict): A map of variable names to JSONPath expressions that will be used to pull
                                      the corresponding values out of response JSON.
                      wait_for_success (bool|dict): (optional, default false) If true, requests will be retried
                                                    until a success response is returned. If the dict form is
                                                    given, the following configuration options are supported:
                                                    - delay: (number, default 5) Time in seconds to wait before
                                                             trying the request. The delay will be applied before
                                                             every attempt, including the first one.
                                                    - attempts: (number, default 3) The number of times to try the
                                                                request before giving up. On failure, the last
                                                                response returned will be exposed.
                      All values support template substitutions except "method", "description" and "outputs".
            :argument parent (Context) The parent context, typically the Flow, provides substitution values.
        """
        super().__init__(parent=parent)
        self.step_name = step_name
        self.step_definition = step_definition
        self.step_description = self.step_definition.get('description', self.step_name)
        self.step_method = self.step_definition.get('method', 'GET')
        self.step_request = Request(self)
        self.step_retry_config = self._get_retry_config()
        if parent is not None:
            setattr(parent, self.step_name, self)

    def _gather_outputs(self):
        """ After the request is completed, every key in the "outputs" section of the step is evaluated as a
            JSONPath against the response json, and the result stored as properties on the object. """
        outputs = dict(map(
            lambda match: (
                match[0],
                match[1][0] if len(match[1]) == 1 else match[1],
            ),
            map(
                lambda output: (
                    output[0],
                    list(map(
                        lambda v: v.value,
                        parse(output[1]).find(self.step_request.response_body)
                    ))
                ),
                self.step_definition.get('outputs', {}).items()
            )
        )) if isinstance(self.step_request.response_body, dict) else {}
        if outputs:
            print('\n===== STEP OUTPUTS =====')
            for item in outputs.items():
                setattr(self, *item)
                print(f'{item[0]}: {item[1]}')

    def _generate_attempts(self):
        attempt_count = self.step_retry_config.attempt
        delay_in_seconds = self.step_retry_config.delay

        attempt = 0
        succeeded = False
        while attempt < attempt_count and not succeeded:
            attempt = attempt + 1
            print(f'(Attempt {attempt}/{attempt_count})')
            if delay_in_seconds > 0:
                time.sleep(delay_in_seconds)
            succeeded = self.step_request.execute()
            yield succeeded

    def _get_retry_config(self):
        wait_for_success = self.step_definition.get('wait_for_success', False)
        wait_for_success = {
            **RETRY,
            **wait_for_success
        } if isinstance(wait_for_success, ComplexNamespace) else (
            RETRY if wait_for_success else RUN_ONCE
        )
        return ComplexNamespace(**wait_for_success)

    def execute(self):
        """ Run the API request and make the outputs available.
            This will be triggered automatically by accessing the "response" attribute if the request has not yet been
            run.  The "requests" response object is stored on the step object itself.
        """
        print(f'\nExecuting step {self.step_description} of flow {self.flow_description}')
        self.flow_store.current_step = self
        if reduce(lambda r, v: r or v, self._generate_attempts(), False):
            self._gather_outputs()
            self.flow_store.previous_step = self
            self.flow_store.current_step = None
        print(f'Completed step {self.step_description}\n')
        return self.step_request.response_succeeded

    step_body = property(
        lambda self: Template.interpolate(
            self.step_definition.get('body'),
            self
        )
    )
    step_headers = property(
        lambda self: Template.interpolate(
            self.step_definition.get('headers', {}),
            self
        )
    )
    step_url = property(
        lambda self: Template.interpolate(
            self.step_definition['url'],
            self
        )
    )
