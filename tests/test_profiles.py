import pytest
from unittest.mock import patch
from api_flow.config import Config
from api_flow.complex_namespace import ComplexNamespace
from api_flow.profiles import Profiles


@pytest.fixture(autouse=True)
def mock_profile_path():
    Config.profile_path = '/profile'
    yield
    Config.profile_path = None


@pytest.fixture
def mock_from_yaml():
    with patch.object(ComplexNamespace, 'from_yaml') as mock_from_yaml:
        yield mock_from_yaml


@pytest.fixture
def mock_load_profiles():
    with patch.object(Profiles, '_load_profiles') as mock_load_profiles:
        yield mock_load_profiles


@pytest.fixture
def mock_from_yaml():
    with patch('api_flow.complex_namespace.ComplexNamespace.from_yaml') as mock_from_yaml:
        def side_effect(file_path):
            print(file_path)
            return ComplexNamespace()
        mock_from_yaml.side_effect = side_effect
        yield mock_from_yaml


class TestProfiles:
    def test_loads_single_profile(self, mock_from_yaml):
        profiles = Profiles(profile='foo')
        mock_from_yaml.assert_any_call('/profile/foo.yaml')

    def test_loads_multiple_profiles(self, mock_from_yaml):
        profiles = Profiles(profiles=['foo', 'bar'])
        mock_from_yaml.assert_any_call('/profile/foo.yaml')
        mock_from_yaml.assert_any_call('/profile/bar.yaml')

    def test_combines_profiles(self, mock_from_yaml):
        profiles = Profiles(profile='baz', profiles=['foo', 'bar'])
        mock_from_yaml.assert_any_call('/profile/foo.yaml')
        mock_from_yaml.assert_any_call('/profile/bar.yaml')
        mock_from_yaml.assert_any_call('/profile/baz.yaml')

    def test__load_profiles(self, mock_from_yaml):
        mock_from_yaml.side_effect = [
            ComplexNamespace(a='A', b='B'),
            ComplexNamespace(b='B2', c='C'),
        ]
        profiles = Profiles(profiles=['bogus', 'bogus2'])
        assert profiles.a == 'A'
        assert profiles.b == 'B2'
        assert profiles.c == 'C'
