import os
import pytest
from unittest.mock import patch
from api_flow.complex_namespace import ComplexNamespace
from api_flow.context import Context


@pytest.fixture
def mock_from_yaml():
    with patch.object(ComplexNamespace, 'from_yaml') as mock_from_yaml:
        yield mock_from_yaml


@pytest.fixture(autouse=True)
def clear_globals():
    Context.GLOBALS = ComplexNamespace()
    if os.environ.get('foo') is not None:
        del os.environ['foo']
    yield
    Context.GLOBALS = ComplexNamespace()
    if os.environ.get('foo') is not None:
        del os.environ['foo']


class TestContext:
    def test_precedence(self):
        context = Context()
        with pytest.raises(AttributeError):
            context.value
        setattr(context, 'parent', Context(value='inherited'))
        assert context.value == 'inherited'
        Context.GLOBALS.value = 'global'
        assert context.value == 'global'
        os.environ['value'] = 'environment'
        assert context.value == 'environment'
        context.value = 'self'
        assert context.value == 'self'

    def test_hasattr_none(self):
        context = Context()
        assert not hasattr(context, 'foo')

    def test_hasattr_parent(self):
        context = Context(parent=Context(foo='v'))
        assert hasattr(context, 'foo')

    def test_hasattr_global(self):
        Context.GLOBALS.foo = 'v'
        context = Context()
        assert hasattr(context, 'foo')

    def test_hasattr_environment(self):
        os.environ['foo'] = 'v'
        context = Context()
        assert hasattr(context, 'foo')

    def test_hasattr_self(self):
        context = Context(foo='V')
        assert hasattr(context, 'foo')

    def test_set_global(self):
        parent = Context()
        child = Context(parent=parent)
        parent.set_global('parent_global', 'PARENT')
        child.set_global('child_global', 'CHILD')
        assert parent.child_global == 'CHILD'
        assert child.parent_global == 'PARENT'
