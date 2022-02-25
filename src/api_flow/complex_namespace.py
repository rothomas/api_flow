import yaml
from types import SimpleNamespace


class ComplexNamespace(SimpleNamespace):
    """
    Extends SimpleNamespace with recursive transformation of nested dicts.
    Enables universal dot-notation syntax in template tags.
    """

    @staticmethod
    def from_yaml(file_path, exit_on_error=True):
        """
        Wraps yaml.safe_load with error handling to log and exit.
        :param file_path: The file path to load.
        :param exit_on_error: (boolean, default True) Terminate immediately on error?
        :return: A ComplexNamespace containing deserialized YAML content.
        """
        with open(file_path, 'r') as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                if not isinstance(yaml_data, dict):
                    raise ValueError('YAML configuration documents for api_flow are expected to be dictionaries.')
                return ComplexNamespace(**yaml_data)
            except ValueError as e:
                print(f'Unexpected YAML config in {file_path}: {str(e)}')
                if exit_on_error:
                    exit(1)
            except yaml.YAMLError as e:
                print(f'YAML parsing error in {file_path}\n{str(e)}')
                if exit_on_error:
                    exit(1)

    def __init__(self, **kwargs):
        """
        Constructor for ComplexNamespace
        :param kwargs: optional splatted dict of source data
        """
        super().__init__(**dict(map(self.upgrade_dict_mapper, kwargs.items())))

    def __getattr__(self, key):
        """
        Override for basic __getattr__ behavior. This forwards
        all __dict__ methods to the class, so that a ComplexNamespace
        behaves as either a class or a dict.
        :param key:  the key to retrieve
        :return: the requested value, if any
        :raise: AttributeError if no such key found.
        """
        if hasattr(self.__dict__, key):
            return getattr(self.__dict__, key)
        return getattr(super(), key)

    def __getitem__(self, key):
        """
        Even though we are proxying the dict interface to __dict__ above,
        __getitem__ is the minimum interface that must be directly implemented
        on the class for it to be recognized as dict-like.
        :param key: the subscript key
        :return: the value, if any.
        :raise: KeyError if no such key
        """
        return self.__dict__.__getitem__(key)

    def __setattr__(self, key, value):
        """
        Overrides set to recursively transform dict values into namespaces on assignment.
        :param key: the attribute name
        :param value: the value to transform and set
        """
        super().__setattr__(key, self.upgrade_dict(value))

    def as_dict(self):
        return self.downgrade_value(self)

    def downgrade_value(self, value):
        if isinstance(value, ComplexNamespace):
            return dict(
                map(
                    lambda item: (item[0], self.downgrade_value(item[1])),
                    value.items()
                )
            )
        elif isinstance(value, list):
            return list(map(self.downgrade_value, value))
        return value

    def upgrade_dict(self, value):
        """
        Given a value, checks types and, if appropriate, upgrades dicts to ComplexNamespaces.
        :param value: any value
        :returns: the same value with nested dicts transformed to ComplexNamespaces as needed.
        """
        if isinstance(value, dict):
            return ComplexNamespace(**value)
        elif isinstance(value, list):
            return list(map(self.upgrade_dict, value))
        return value

    def upgrade_dict_mapper(self, item):
        """
        Wraps upgrade_dict in a function that can be passed directly to map() for dicts.
        :param item: a (key, value) tuple returned from dict.items()
        :returns: the same tuple with the value transformed via upgrade_dict.
        """
        (key, value) = item
        return key, self.upgrade_dict(value)

    def merge(self, other):
        """
        Add the contents of another ComplexNamespace to this one.  Conflicts
        are resolved in favor of 'other'.
        :param other: (ComplexNamespace) the other namespace to merge in
        :return: self
        """
        self.__dict__.update(other.__dict__)
        return self

