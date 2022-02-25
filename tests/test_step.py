import pytest
from api_flow.context import Context
from api_flow.step import Step, DEFAULT_ATTEMPT_COUNT, DEFAULT_DELAY_SECONDS
from unittest.mock import patch


@pytest.fixture
def mock_request():
    with patch('api_flow.step.Request', autospec=True) as mock_request:
        mock_request.return_value.execute.side_effect = [False, False, True]
        mock_request.return_value.response_body = {
            'foo': 'FOO',
            'bar': 'BAR',
            'baz': 'BAZ',
        }
        mock_request.return_value.response_succeeded = True
        yield mock_request


@pytest.fixture
def mock_sleep():
    with patch('time.sleep') as mock_sleep:
        yield mock_sleep


@pytest.fixture
def mock_parent_flow():
    yield Context(
        flow_description='Mock Parent Flow',
        flow_store=Context()
    )


class TestStep:
    def test_retry_config_boolean_true(self, mock_parent_flow):
        step = Step('name', {
            'wait_for_success': True
        }, parent=mock_parent_flow)
        assert step.step_retry_config.attempt == DEFAULT_ATTEMPT_COUNT
        assert step.step_retry_config.delay == DEFAULT_DELAY_SECONDS

    def test_retry_config_boolean_false(self, mock_parent_flow):
        step = Step('name', {
            'wait_for_success': False
        }, parent=mock_parent_flow)
        assert step.step_retry_config.attempt == 1
        assert step.step_retry_config.delay == 0

    def test_retry_config_empty_dict(self, mock_parent_flow):
        step = Step('name', {
            'wait_for_success': {}
        }, parent=mock_parent_flow)
        assert step.step_retry_config.attempt == DEFAULT_ATTEMPT_COUNT
        assert step.step_retry_config.delay == DEFAULT_DELAY_SECONDS

    def test_retry_config_full_dict(self, mock_parent_flow):
        step = Step('name', {
            'wait_for_success': {
                'attempt': 10,
                'delay': 15
            }
        }, parent=mock_parent_flow)
        assert step.step_retry_config.attempt == 10
        assert step.step_retry_config.delay == 15

    def test_retry_config_attempt_only(self, mock_parent_flow):
        step = Step('name', {
            'wait_for_success': {
                'attempt': 10
            }
        }, parent=mock_parent_flow)
        assert step.step_retry_config.attempt == 10
        assert step.step_retry_config.delay == DEFAULT_DELAY_SECONDS

    def test_retry_config_delay_only(self):
        step = Step('name', {
            'wait_for_success': {
                'delay': 15
            }
        })
        assert step.step_retry_config.attempt == DEFAULT_ATTEMPT_COUNT
        assert step.step_retry_config.delay == 15

    def test_execute(self, mock_request, mock_sleep, mock_parent_flow):
        step = Step('name', {
            'url': 'https://test',
            'description': 'DESCRIPTION',
            'wait_for_success': {
                'attempt': 3,
                'delay': 8,
            },
            'outputs': {
                'foo': '$.foo',
                'bar': '$.bar',
                'baz': '$.baz',
            }
        }, parent=mock_parent_flow)
        assert step.execute()
        mock_sleep.assert_any_call(8)  # other things call sleep here
        assert step.foo == 'FOO'
        assert step.bar == 'BAR'
        assert step.baz == 'BAZ'
