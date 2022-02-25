import os
import pytest
from api_flow.config import Config


@pytest.fixture(autouse=True)
def fresh_config():
    yield
    if os.environ.get('DATA_PATH'):
        del os.environ['DATA_PATH']
    if os.environ.get('PROFILE_PATH'):
        del os.environ['PROFILE_PATH']
    if os.environ.get('FLOW_PATH'):
        del os.environ['FLOW_PATH']
    if os.environ.get('TEMPLATE_PATH'):
        del os.environ['TEMPLATE_PATH']
    if os.environ.get('FUNCTION_PATH'):
        del os.environ['FUNCTION_PATH']
    Config.data_path = None
    Config.profile_path = None
    Config.flow_path = None
    Config.template_path = None
    Config.function_path = None


class TestConfig:
    def test_setters_set_all(self):
        Config.data_path = '/tmp'
        Config.profile_path = '/tmp/something/profile'
        Config.flow_path = '/tmp/whatever/flows'
        Config.template_path = '/tmp/nowhere/templates'
        Config.function_path = '/tmp/funky/functions'
        assert Config.data_path == '/tmp'
        assert Config.profile_path == '/tmp/something/profile'
        assert Config.flow_path == '/tmp/whatever/flows'
        assert Config.template_path == '/tmp/nowhere/templates'
        assert Config.function_path == '/tmp/funky/functions'

    def test_defaults(self):
        assert Config.data_path == os.path.abspath('.')
        assert Config.profile_path == os.path.abspath('./profiles')
        assert Config.flow_path == os.path.abspath('./flows')
        assert Config.template_path == os.path.abspath('./templates')
        assert Config.function_path == os.path.abspath('./functions')

    def test_alt_data_path(self):
        Config.data_path = '/tmp'
        assert Config.data_path == '/tmp'
        assert Config.profile_path == '/tmp/profiles'
        assert Config.flow_path == '/tmp/flows'
        assert Config.template_path == '/tmp/templates'
        assert Config.function_path == '/tmp/functions'

    def test_configure_from_environment(self, fresh_config):
        os.environ['DATA_PATH'] = '/tmp'
        os.environ['PROFILE_PATH'] = '/tmp/something/profile'
        os.environ['FLOW_PATH'] = '/tmp/whatever/flows'
        os.environ['TEMPLATE_PATH'] = '/tmp/nowhere/templates'
        os.environ['FUNCTION_PATH'] = '/tmp/funky/functions'
        assert Config.data_path == '/tmp'
        assert Config.profile_path == '/tmp/something/profile'
        assert Config.flow_path == '/tmp/whatever/flows'
        assert Config.template_path == '/tmp/nowhere/templates'
        assert Config.function_path == '/tmp/funky/functions'

