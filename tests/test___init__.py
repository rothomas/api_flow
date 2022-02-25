import pytest
from unittest.mock import patch
from api_flow.config import Config
from api_flow import configure, execute


@pytest.fixture(autouse=True)
def setup_config():
    Config.data_path = '/data'
    Config.flow_path = None
    Config.function_path = None
    Config.profile_path = None
    Config.template_path = None
    yield
    Config.data_path = None
    Config.flow_path = None
    Config.function_path = None
    Config.profile_path = None
    Config.template_path = None


@pytest.fixture
def mock_flow():
    with patch('api_flow.Flow') as mock_flow:
        yield mock_flow


class TestInit:
    def test_configure(self):
        assert Config.data_path == '/data'
        assert Config.flow_path == '/data/flows'
        assert Config.function_path == '/data/functions'
        assert Config.profile_path == '/data/profiles'
        assert Config.template_path == '/data/templates'
        configure(flow_path='/flows', profile_path='/profiles')
        assert Config.flow_path == '/flows'
        assert Config.function_path == '/data/functions'
        assert Config.profile_path == '/profiles'
        assert Config.template_path == '/data/templates'
        configure(function_path='/functions', template_path='/templates')
        assert Config.flow_path == '/flows'
        assert Config.function_path == '/functions'
        assert Config.profile_path == '/profiles'
        assert Config.template_path == '/templates'
        configure(data_path='/somewhere')
        assert Config.data_path == '/somewhere'
        assert Config.flow_path == '/flows'
        assert Config.function_path == '/functions'
        assert Config.profile_path == '/profiles'
        assert Config.template_path == '/templates'

    def test_execute(self, mock_flow):
        flow = execute('my_flow', profile='p', profiles=['q', 'r'])
        flow.execute.assert_called()

