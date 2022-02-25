import os


class _Config:
    """
    Class for configuring the data directories for api-flow. Defaults are relative to the current directory,
    and can be overridden either by setting the attributes here or by providing environment variables. This class
    is protected and an instance is exposed as the Config export to provide singleton behavior.
    """
    _data_path = None
    _profile_path = None
    _flow_path = None
    _template_path = None
    _function_path = None

    def __init__(self):
        pass

    def configure(self, data_path=None, flow_path=None, function_path=None, profile_path=None, template_path=None):
        if data_path is not None:
            self.data_path = data_path
        if flow_path is not None:
            self.flow_path = flow_path
        if function_path is not None:
            self.function_path = function_path
        if profile_path is not None:
            self.profile_path = profile_path
        if template_path is not None:
            self.template_path = template_path

    def get_data_path(self):
        """
        Getter for the base data path. Default values for other paths are relative to this one.
        Can be overridden by the DATA_PATH environment variable.
        :return: The configured or inferred data directory.
        """
        return self.__class__._data_path or os.environ.get('DATA_PATH', os.path.abspath('.'))

    def set_data_path(self, path):
        """
        Setter for the base data path. Default values for other paths are relative to this one.
        :param path: The base path to look in for configuration data directories.
        :return: nothing
        """
        self.__class__._data_path = path

    def get_profile_path(self):
        """
        Getter for the profile path. Defaults to "{data_path}/profiles".
        Can be overridden by the PROFILE_PATH environment variable.
        :return: The configured or inferred profile directory.
        """
        return self.__class__._profile_path or os.environ.get(
            'PROFILE_PATH', os.path.join(self.data_path, 'profiles')
        )

    def set_profile_path(self, path):
        """
        Setter for the profile path. If set, the directory location is independent of the data_path value.
        :param path: The new profile path.
        :return: nothing
        """
        self.__class__._profile_path = path

    def get_flow_path(self):
        """
        Getter for the flow path. Defaults to "{data_path}/flows".
        Can be overridden by the FLOW_PATH environment variable.
        :return: The configured or inferred flow directory.
        """
        return self.__class__._flow_path or os.environ.get(
            'FLOW_PATH', os.path.join(self.data_path, 'flows')
        )

    def set_flow_path(self, path):
        """
        Setter for the flow path. If set, the directory location is independent of the data_path value.
        :param path: The new flow path.
        :return: nothing
        """
        self.__class__._flow_path = path

    def get_template_path(self):
        """
        Getter for the template path. Defaults to "{data_path}/templates".
        Can be overridden by the TEMPLATE_PATH environment variable.
        :return: The configured or inferred template directory.
        """
        return self.__class__._template_path or os.environ.get(
            'TEMPLATE_PATH', os.path.join(self.data_path, 'templates')
        )

    def set_template_path(self, path):
        """
        Setter for the template path. If set, the directory location is independent of the data_path value.

        :param path: The new template path.
        :return: nothing
        """
        self.__class__._template_path = path

    def get_function_path(self):
        """
        Getter for the function path. Defaults to "{data_path}/functions".
        Can be overridden by the FUNCTION_PATH environment variable.
        :return: The configured or inferred function directory.
        """
        return self.__class__._function_path or os.environ.get(
            'FUNCTION_PATH', os.path.join(self.data_path, 'functions')
        )

    def set_function_path(self, path):
        """
        Setter for the function path. If set, the directory location is independent of the data_path value.

        :param path: The new function path.
        :return: nothing
        """
        self.__class__._function_path = path

    data_path = property(get_data_path, set_data_path)
    profile_path = property(get_profile_path, set_profile_path)
    flow_path = property(get_flow_path, set_flow_path)
    function_path = property(get_function_path, set_function_path)
    template_path = property(get_template_path, set_template_path)


Config = _Config()
