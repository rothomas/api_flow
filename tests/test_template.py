import os
import pytest
from api_flow.config import Config
from api_flow.context import Context
from api_flow.template import Template


@pytest.fixture(autouse=True)
def set_function_path():
    Config.data_path = os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture
def mock_context():
    return Context(**{
        "list_value": [
            "a",
            "b",
            "c",
        ],
        "dict_value": {
            "d": "D",
            "e": "E",
            "f": {
                "g": "G",
            },
        },
        "str_value": "H",
    })


class TestTemplate:
    def test_template_cannot_instantiate(self):
        with pytest.raises(TypeError):
            Template()

    def test_unsupported_value_type(self, mock_context):
        assert Template.interpolate(123, mock_context) == 123

    def test_str(self):
        s = Template.interpolate_str('{? a ?}', Context(a='A'))
        assert s == 'A'

    def test_interpolate(self, mock_context):
        output = Template.interpolate({
            'str': 'The values are {? list_value[0] ?}, {? dict_value.d ?}, {? str_value ?}, {? echo("TESTFN") ?}, '
                   '{? non_existent_function() ?}',
            'list': [
                '{? list_value[1] ?}',
                '{? dict_value.e ?}',
                '{? str_value ?}',
                '{? echo("TESTFN") ?}',
                '{? non_existent_function() ?}',
                'template:test_template.txt',
            ],
            'dict': {
                'one': '{? list_value[2] ?}',
                'two': '{? dict_value.f.g ?}',
                'three': '{? str_value ?}',
                'four': '{? echo("TESTFN") ?}',
                'five': '{? non_existent_function() ?}',
                'six': 'template:test_template.txt',
            }
        }, mock_context)
        assert output['str'] == 'The values are a, D, H, TESTFN, '
        assert output['list'] == [
            'b',
            'E',
            'H',
            'TESTFN',
            '',
            'The value is H.\n'
        ]
        assert output['dict'] == {
            'one': 'c',
            'two': 'G',
            'three': 'H',
            'four': 'TESTFN',
            'five': '',
            'six': 'The value is H.\n'
        }
