import os
import pytest
import yaml
from unittest.mock import patch
from api_flow.complex_namespace import ComplexNamespace
from io import StringIO
from yaml import YAMLError


MOCK_YAML_FILE = '''
a:
  b:
    c: 'D'
e:
  - f
  - g
  - h:
      i: j
      k:
        l: m
        n:
          - o: p
'''


@pytest.fixture
def mock_open():
    with patch('builtins.open') as open_func:
        yield open_func


@pytest.fixture
def mock_exit():
    with patch('builtins.exit') as exit_func:
        yield exit_func


@pytest.fixture
def mock_yaml_load():
    with patch('yaml.safe_load') as yaml_load_func:
        yield yaml_load_func


class TestComplexNamespace:
    def test_from_yaml(self, mock_open, mock_exit):
        mock_open.return_value = StringIO(MOCK_YAML_FILE)
        y = ComplexNamespace.from_yaml('/bogus')
        assert y.a.b.c == 'D'
        assert y.e[0] == 'f'
        assert y.e[1] == 'g'
        assert y.e[2].h.i == 'j'
        assert y.e[2].h.k.l == 'm'
        assert y.e[2].h.k.n[0].o == 'p'
        mock_exit.assert_not_called()

    def test_construction(self):
        mock_yaml = StringIO(MOCK_YAML_FILE)
        y = ComplexNamespace(**yaml.safe_load(mock_yaml))
        assert y.a.b.c == 'D'
        assert y.e[0] == 'f'
        assert y.e[1] == 'g'
        assert y.e[2].h.i == 'j'
        assert y.e[2].h.k.l == 'm'
        assert y.e[2].h.k.n[0].o == 'p'

    def test_assignment(self):
        mock_yaml = yaml.safe_load(StringIO(MOCK_YAML_FILE))
        y = ComplexNamespace()
        y.e = mock_yaml['e']
        assert y.e[0] == 'f'
        assert y.e[1] == 'g'
        assert y.e[2].h.i == 'j'
        assert y.e[2].h.k.l == 'm'
        assert y.e[2].h.k.n[0].o == 'p'

    def test_from_yaml_fails_value_error(
        self,
        mock_open,
        mock_exit,
        mock_yaml_load
    ):
        mock_yaml_load.side_effect = ValueError()
        ComplexNamespace.from_yaml('/bogus')
        mock_exit.assert_called_with(1)

    def test_from_yaml_fails_value_error_no_exit_flag(
        self,
        mock_open,
        mock_exit,
        mock_yaml_load
    ):
        mock_yaml_load.side_effect = ValueError()
        ComplexNamespace.from_yaml('/bogus', exit_on_error=False)
        mock_exit.assert_not_called()

    def test_from_yaml_fails_yaml_error(
        self,
        mock_open,
        mock_exit,
        mock_yaml_load
    ):
        mock_yaml_load.side_effect = YAMLError()
        ComplexNamespace.from_yaml('/bogus')
        mock_exit.assert_called_with(1)

    def test_from_yaml_fails_yaml_error_no_exit_flag(
        self,
        mock_open,
        mock_exit,
        mock_yaml_load
    ):
        mock_yaml_load.side_effect = YAMLError()
        ComplexNamespace.from_yaml('/bogus', exit_on_error=False)
        mock_exit.assert_not_called()

    def test_from_yaml_fails_when_not_dict(
        self,
        mock_open,
        mock_exit,
        mock_yaml_load
    ):
        mock_yaml_load.return_value = "This Is Not OK"
        ComplexNamespace.from_yaml('/bogus')
        mock_exit.assert_called_with(1)

    def test_merge(self):
        first = ComplexNamespace(foo="Foo", bar="Bar")
        second = ComplexNamespace(bar="Bar2", baz="Baz")
        first.merge(second)
        assert first.foo == 'Foo'
        assert first.bar == 'Bar2'
        assert first.baz == 'Baz'

    def test_exposes_dict_behavior(self):
        ns = ComplexNamespace(foo='Foo', bar='Bar', baz='Baz')
        assert ns.foo == 'Foo'
        assert ns['foo'] == 'Foo'
        assert list(ns.keys()) == ['foo', 'bar', 'baz']
        assert list(ns.values()) == ['Foo', 'Bar', 'Baz']

    def test_downgrade(self):
        item = ComplexNamespace(
            dictval={
                'a': 'A',
                'b': 'B',
                'c': 'C',
                'listval': ['D', 'E', 'F'],
            },
            listval=[
                {'g': 'G', 'h': 'H', 'i': 'I'},
                'J',
                'K'
            ],
            strval='L',
        )
        assert item.as_dict() == {
            'dictval': {
                'a': 'A',
                'b': 'B',
                'c': 'C',
                'listval': ['D', 'E', 'F'],
            },
            'listval': [
                {'g': 'G', 'h': 'H', 'i': 'I'},
                'J',
                'K'
            ],
            'strval': 'L'
        }
