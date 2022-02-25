from api_flow.config import Config
from api_flow.context import Context
from api_flow.flow import Flow
from api_flow.profiles import Profiles


def configure(data_path=None, flow_path=None, function_path=None, profile_path=None, template_path=None):
    """ Shortcut method to configure resource paths for api_flow
        See Config.configure
    """
    Config.configure(data_path, flow_path, function_path, profile_path, template_path)


def execute(flow_name, profile=None, profiles=None, **kwargs):
    """ Shortcut to create and execute a flow.
        See Flow.__init__ and Flow.execute
    """
    flow_instance = Flow(flow_name, profile=profile, profiles=profiles, **kwargs)
    flow_instance.execute()
    return flow_instance
