import os
import pytest
import re
from api_flow.config import Config
from api_flow.functions import get_template_function, random, uuid


@pytest.fixture(autouse=True)
def set_function_path():
    Config.data_path = os.path.join(os.path.dirname(__file__), 'test_data')
    yield
    Config.data_path = None


class TestFunctions:
    def test_get_template_function_will_not_load_self(self):
        with pytest.raises(ValueError):
            get_template_function('get_template_function')

    def test_get_template_function_loads_builtin(self):
        uuid = get_template_function('uuid')
        assert uuid.__class__.__name__ == 'function'

    def test_get_template_function_loads_user(self):
        echo = get_template_function('echo')
        assert echo.__class__.__name__ == 'function'

    def test_get_template_function_handles_missing(self):
        missing = get_template_function('missing_function')
        assert missing is None

    def test_random(self):
        random_number = random(None, 100000)
        assert re.compile(r'^[0-9]{5}$').match(random_number) is not None

    def test_uuid(self):
        uuid_str = uuid(None)
        uuid_regexp = re.compile(
            r'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$'
        )
        assert uuid_regexp.match(uuid_str) is not None
