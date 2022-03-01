import json
import os
import re
from api_flow.functions import get_template_function
from api_flow.config import Config
from api_flow.complex_namespace import ComplexNamespace


class Template:
    """
    class responsible for performing template replacements
    (using {? this_format ?}) in YAML files and JSON templates

    The class resists instantiation. Entrypoint is *Template.interpolate*.
    """

    SUBSTITUTION = re.compile(r'{\?\s*([^?]*\S)\s*\?}')
    FUNCTION_CALL = re.compile(r'^([a-z][a-z_0-9]*)\((.*)\)$')
    TEMPLATE_TAG = re.compile(r'^template:(.*)$')

    def __init__(self):
        raise TypeError(
            'Template is not an instantiated class. See Template.interpolate.'
        )

    @classmethod
    def _get_value_renderer(cls, context):
        """
        *Pattern.sub* can take a function that receives a regex Match object
        and returns the substituted value, allowing dynamic substitutions.
        This method constructs a substitution function that replaces a
        value with values defined in the supplied context.

        :param context: Any context object (usually a Step) containing
                        substitution values.
        :type context: Context
        :return: a function that will be used to perform replacements on a
                 regex match
        """
        def render(substitution):
            """
            A regex "Pattern.sub" match handler that replaces a substitution
            with the appropriate values

            :param substitution: the template tag match object
            :type substitution: re.Match
            :return: the appropriate substitution from the context
            :rtype: str
            """
            function_match = cls.FUNCTION_CALL.match(substitution.group(1))
            if function_match is not None:
                return cls._render_function(function_match, context)
            else:
                return cls._render_value(substitution.group(1), context)
        return render

    @classmethod
    def interpolate(cls, value, context):
        """
        Given any value, perform variable interpolations if the value's type
        is supported. Currently-supported data types are str (basic
        substitution), list (perform substitution on all elements) and
        dict (perform substitution on all values).

        :param value: the value in which to replace substitution tags
        :type value: Any
        :param context: the source of the substitution data
        :type context: Context
        :return: value with all substitutions made
        :rtype: Any
        """
        if isinstance(value, str):
            return cls.interpolate_str(value, context)
        elif isinstance(value, list):
            return cls._interpolate_list(value, context)
        elif isinstance(value, dict):
            return cls._interpolate_dict(value, context)
        elif isinstance(value, ComplexNamespace):
            return cls._interpolate_dict(value.as_dict(), context)
        return value

    @classmethod
    def _interpolate_dict(cls, value, context):
        """
        Called from "interpolate" to act on dict values.

        :param value: a dictionary whose values are to be interpolated
        :type value: dict
        :param context: the source of substitution data
        :type context: Context
        :return: value dict with substitutions performed
        :rtype: dict
        """
        return dict(
            map(
                lambda item: (item[0], cls.interpolate(item[1], context)),
                value.items()
            )
        )

    @classmethod
    def _interpolate_list(cls, value, context):
        """
        Called from "interpolate" to act on list values.

        :param value: the list whose members are to be interpolated
        :type value: list
        :param context: the source of substitution values
        :type context: Context
        :return: value with members interpolated
        :rtype: list
        """
        return list(
            map(
                lambda item: cls.interpolate(item, context),
                value
            )
        )

    @classmethod
    def interpolate_str(cls, value, context):
        """
        Called by "interpolate" to replace substitution tags in strings.

        :param value: a string possibly containing substitution tags
        :type value: str
        :param context: the source of substitution data
        :type context: Context
        :return: value with all substitution tags replaced
        :rtype: str
        """
        match = cls.TEMPLATE_TAG.fullmatch(value)
        if match is not None:
            value = open(
                os.path.join(
                    Config.template_path,
                    f"{match.group(1)}"
                )
            ).read()
        return cls._render_template(value, context)

    @classmethod
    def _render_function(cls, function_match, context):
        """
        Templates can call simple functions to produce dynamic values. At
        present this is highly limited. Nested function calls are not
        supported, and neither are nested template substitutions of arguments.
        Arguments must decode as JSON values, because that's how they are
        decoded to pass to the function.

        :param function_match: (re.Match) the regex match containing a
                               function call
        :param context: (Context) the context object to supply
        :return: return value from the indicated function call as str
        """
        function = get_template_function(function_match.group(1))
        if function is not None:
            args = []
            if len(function_match.group(2).strip()) > 0:
                args = json.loads(f'[{function_match.group(2)}]')
            return str(function(context, *args))
        return ''

    @classmethod
    def _render_template(cls, template, context):
        """ Replaces every substitution tag in a template with the correct
            context value

            :param template: (str) the source template to render
            :param context: (Context) the object containing substitution
                               values
            :return the template with substitutions performed
        """
        return cls.SUBSTITUTION.sub(cls._get_value_renderer(context), template)

    @classmethod
    def _render_value(cls, name, context):
        if not name.startswith('context.'):
            name = f'context.{name}'
        return f'{{{name}}}'.format(context=context)

