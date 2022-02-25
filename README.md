# api-flow
This utility allows the user to define, in YAML, “flows” composed of “steps,” each of which performs a single REST API 
request, and execute them.

## Configuration
`api-flow` pulls configuration from files in a few directories.  These have default values within the current directory 
when running the script, can be specified by environment variables, or can be explicitly set programmatically.
### Data Path
If all other configuration files live under a common directory, either set Config().environment_path or set the
`DATA_PATH` environment variable.  The default is the current directory when executing the script.
### Environments
This is the directory from which base environment definitions are loaded.  The files inside it must be in YAML format, 
and load to a dictionary of variables/values.  The default location is `{DATA_PATH}/environments` but can be overridden 
with by setting `Config.environment_path` or the `ENVIRONMENT_PATH` environment variable.  If the environment is not
configured, it defaults to an empty dictionary, so any values your requests need must be provided in another way.
### Flows
This is the directory containing the flow+step definitions in YAML format. The files inside it must be in YAML format, 
and load to a dictionary of variables/values.  The default location is `{DATA_PATH}/flows` but can be overridden 
with by setting `Config.environment_path` or the `ENVIRONMENT_PATH` environment variable. A flow can contain the
following:
-`depends_on`: A list of strings describing other flows that must be run, in order, to populate the context for this 
               flow to execute.
- `description`: A human-readable string describing the flow.
- `steps`: An ordered dictionary of steps for the flow.  Steps can contain the following values:
      - `description`: A human-readable description of the step
      - `url`: (required) The URL to request
      - `method`: (default GET) The HTTP request method to use.
      - `headers`: A dict of key/value pairs sent as request headers.
      - `body`: The body to be sent with a POST/PUT/PATCH etc request.  This can be defined in YAML format but will be
                translated to JSON in the request.  Defining the body as stringified JSON (with `{?…?}` templating) 
                should also be supported.
      - `output`: A dictionary of variables that should be extracted from the response data.  The key is the variable name, and the value is a `jsonpath` expression describing the path in the response data to the desired value, which can be a single result or list of results depending on the query.  These values are available to subsequent steps via the standard templating.
### Templates
This directory contains a collection of body (or other) templates in JSON format.  It defaults to
`{DATA_PATH}/templates` but can be overridden by the `TEMPLATES_PATH` environment variable.  You can reference a
template file in flow configuration by using the value `template:template_name` in the flow YAML.  So you can define a
flow step where the body is a template:

## Running as a Module
api-flow currently has a hard coded environment and flow name in `api-flow.py`.  Future modifications will make these configurable.  For now, edit these values in that file to change what is run.

In the api-flow directory run `python -m api-flow` to run the script.

During the run, request and response data will be output to the console for diagnostic purposes.

## Importing api-flow to a project
You can use api-flow from within other code.  Place the api-flow directory in the root of your project so that you can 
import from it.  Use a flow by doing the following:
```python
from api-flow import Flow


flow = Flow('my-flow-name', environment_name='my-environment')
flow.execute()
```
This will load the base environment from `{template_path}/my-environment.yaml` and use that as the base 
environment for a flow loaded from `{flow_path}/my-flow-name.yaml`.

Running `flow.execute()` executes the steps of the flow.  Since you've set `flow` you can access outputs from
individual steps by checking `flow.my-prerequisite.prereq-output-value`.

### Steps
A flow is composed of individual steps, each of which represents a single specific
API request.  Data can be pulled from thre responses of previous steps to compose
the request to the current step.

```
steps:
    my_step:
        url: https://example.com/my_step
        body: template:my_body_template
```

This example would load `my_body_template.json` from the templates directory, interpolate any variable substitutions 
defined in `{?…?}` format, and then use that as the body of the request to `https://example.com/my_step`.
## Context
The context is a collection of variables available to every step in a flow and used for variable substitution in requests.  It is initialized from a base environment, and then each step adds to the context available to subsequent steps.
### Using context variables
Variables extracted from the current context can be used in YAML or JSON files by using the format `{? variable_name ?}`.
Variables are added to the context in the following ways:
### Environment
The base environment is loaded from a YAML file in the `environments` directory.  Give the base name (e.g., `stable_qc`) as the environment name, and the file `stable_qc.yaml` will be loaded as the base set of context values.

Any value specified in the base environment file can be overridden by an environment variable in the OS.
### Prerequisite Flows
If a flow defines a list of `depends_on` flows as prerequisites, those flows will be run, in order, before executing
the specified flow. Those flows are available, by name, on the flow object itself.  For example, if you have a flow
that specifies
```yaml
depends_on:
  - prerequisites
```
before the flow executes, an additional flow, `prerequisites.yaml`, will be loaded from the flows path and run.
That flow will be accessible as `prerequisites` on the flow object, so in templates you can reference
`{? prerequisites.first_prerequisite_step.output_value ?}` and have this resolve to the value generated by
the earlier flow.


### Steps
Each step is accessible in the context, after execution, using its name.  So in the definition of `my_step_2` you can have template values like `{? my_step_1.step_value ?}`.   Values are added according to the `output` section of the step definition.

A special case of step reference is the `previous_step` token.  This can be used in place of the actual step name in template expressions so long as you only need values from the last step to run.


