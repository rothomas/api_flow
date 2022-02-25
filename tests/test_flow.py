import os
import pytest
from api_flow.config import Config
from api_flow.flow import Flow
from api_flow.step import Step
from unittest.mock import patch


@pytest.fixture(autouse=True)
def setup():
    Config.data_path = os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture
def mock_step_execute():
    with patch.object(Step, 'execute') as mock_step_execute:
        mock_step_execute.return_value = True
        yield mock_step_execute


class TestFlow:
    def test___init__(self):
        flow = Flow('multiple_dependencies', profile='foo', profiles=['bar', 'baz'])
        assert flow.flow_name == 'multiple_dependencies'
        assert isinstance(flow.flow_store.multiple_dependencies, Flow)
        assert len(flow.flow_dependencies) == 2
        assert flow.flow_description == 'multiple_dependencies'

    def test_single_dependency(self):
        flow = Flow('single_dependency')
        assert flow.flow_definition.depends_on == 'something_else'
        assert flow.flow_description == 'my single-dependency flow'
        assert len(flow.flow_dependencies) == 1
        assert flow.flow_dependencies[0] == 'something_else'

    def test_execute(self, mock_step_execute):
        flow = Flow('single_dependency')
        assert flow.execute()
        assert flow.flow_dependencies_succeeded
        assert flow.flow_steps_succeeded

    def test_execute_dependencies_fail(self, mock_step_execute):
        flow = Flow('single_dependency')
        flow.flow_store.current_step = Step('bogus_step', {})
        flow.flow_dependencies_succeeded = False
        assert not flow.execute()

    def test_execute_steps_fail(self, mock_step_execute):
        flow = Flow('single_dependency')
        flow.flow_dependencies_succeeded = True
        mock_step_execute.return_value = False
        assert not flow.execute()

    def test_empty_flow_succeeds(self):
        flow = Flow('empty')
        assert flow.execute()
