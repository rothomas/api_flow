import os
from api_flow.complex_namespace import ComplexNamespace


class Context(ComplexNamespace):
    """
    A Context provides the basis for value storage in the API request chain,
    aggregating values from the environment, loaded YAML profiles, other
    context(s) and a set of global values. Flows and steps inherit from Context
    to share and expose data.
    """

    # The GLOBALS data set is used to store values that should have immediate,
    # priority availability to all contexts. The Flow and Step classes use this
    # for making their instances available to other parts of the same request
    # chain. It is not possible to set global variables via the flow
    # configuration. We add things exclusively in the api-flow code itself.
    GLOBALS = ComplexNamespace()

    def __init__(self, parent=None, **kwargs):
        """
        Constructor for Context.

        :param parent: An optional context whose data values are also available
                       to this context. Setting a property in this context
                       will override the same value set in the parent within
                       the scope of this context, but not modify it. Outside
                       the current scope, the parent context value will remain
                       set to whatever it was before.
        :type parent: Context | None
        :param kwargs: the context is initialized with these values
        """
        super().__init__(**kwargs)
        self.parent = parent

    def __getattr__(self, name):
        if name in os.environ:
            return os.environ[name]
        elif hasattr(self.__class__.GLOBALS, name):
            return getattr(self.__class__.GLOBALS, name)
        elif self.parent is not None:
            return getattr(self.parent, name)
        raise AttributeError()

    @staticmethod
    def set_global(name, value):
        setattr(Context.GLOBALS, name, value)
