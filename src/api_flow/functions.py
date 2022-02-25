import os
import random as random_lib
import sys
import uuid as uuid_lib
from importlib.util import spec_from_file_location, module_from_spec
from api_flow.config import Config


"""
Templates for api-flow support simple functions for generating output.
There are a few defined here, but users can define their own by creating
a module and pointing "Config.function_path" to it.

The first parameter to the function is the current context object at
call time (usually a Step, inheriting from a Flow, which has values
loaded from profiles).  The remaining arguments are simple JSON-
encodable values. Only regular args are supported, not kwargs. The
function must return a string, which will be substituted in place of the
function call.
"""


def get_template_function(function_name):
    """
    Resolver for template utility functions.
    The built-in functions take priority over user-defined ones.
    :param function_name: The name of the function to locate.
    :type function_name: str
    :return: the located function, or None
    :rtype: function
    """
    if function_name == 'get_template_function':
        raise ValueError(
            'get_template_function is not a valid name for template functions'
        )

    if function_name in dir(sys.modules[__name__]):
        return getattr(sys.modules[__name__], function_name)

    user_functions_init_path = os.path.join(Config.function_path, '__init__.py')
    if os.path.exists(user_functions_init_path):
        user_functions_spec = spec_from_file_location(
            'user_functions',
            user_functions_init_path,
            submodule_search_locations=[Config.function_path]
        )
        user_functions = module_from_spec(user_functions_spec)
        user_functions_spec.loader.exec_module(user_functions)
        if function_name in dir(user_functions):
            return getattr(user_functions, function_name)

    return None


def random(ctx, max_value):
    """
    Return a random integer in the range [0, max_value) as a fixed-length
    string, left-padded with zeros.
    :param ctx: the context
    :type ctx: Context
    :param max_value: the upper limit on results
    :type max_value: integer
    :return: a fixed-width string representation of a random number
    :rtype: str
    """
    random_lib.seed()
    return str(random_lib.randint(0, max_value)).ljust(len(str(max_value-1)), '0')


def uuid(ctx):
    """
    Return a random UUID
    :return: a new UUID string representation
    :rtype: str
    """
    return str(uuid_lib.uuid4())
