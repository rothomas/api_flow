import json
import pytest
from unittest.mock import MagicMock, patch
from api_flow.request import Request, DEFAULT_HEADERS


@pytest.fixture
def mock_successful_response():
    mock_successful_response = MagicMock()
    mock_successful_response.status_code = 200
    mock_successful_response.headers = {
        'Content-Type': 'application/json'
    }
    mock_successful_response.body.return_value = json.dumps({
        'a': 'A'
    })
    mock_successful_response.ok = True
    yield mock_successful_response


@pytest.fixture
def mock_step():
    mock_step = MagicMock()
    mock_step.step_body = None
    mock_step.step_headers = {
        'Accept': 'application/pdf',
    }
    mock_step.step_url = 'https://test'
    mock_step.step_method = 'GET'
    yield mock_step


@pytest.fixture
def mock_requests_get(mock_successful_response):
    with patch('requests.get') as mock_requests_get:
        mock_requests_get.return_value = mock_successful_response
        yield mock_requests_get


@pytest.fixture
def mock_requests_post(mock_successful_response):
    with patch('requests.post') as mock_requests_post:
        mock_requests_post.return_value = mock_successful_response
        yield mock_requests_post


class TestRequest:
    def test_get_request(self, mock_step, mock_requests_get):
        request = Request(mock_step)
        assert not request.request_executed
        assert not request.response_succeeded
        assert request.execute()
        assert request.request_executed
        assert request.response_succeeded
        mock_requests_get.assert_called_with(
            'https://test',
            headers={
                **DEFAULT_HEADERS,
                'Accept': 'application/pdf',
            }
        )

    def test_get_request_no_response_headers(self, mock_step, mock_successful_response, mock_requests_get):
        request = Request(mock_step)
        mock_successful_response.headers = None
        assert not request.request_executed
        assert not request.response_succeeded
        assert request.execute()
        assert request.request_executed
        assert request.response_succeeded
        mock_requests_get.assert_called_with(
            'https://test',
            headers={
                **DEFAULT_HEADERS,
                'Accept': 'application/pdf',
            }
        )

    def test_get_request_not_a_json_response(self, mock_step, mock_successful_response, mock_requests_get):
        request = Request(mock_step)
        mock_successful_response.body.return_value = 'NOT A JSON DOCUMENT'
        assert not request.request_executed
        assert not request.response_succeeded
        assert request.execute()
        assert request.request_executed
        assert request.response_succeeded
        mock_requests_get.assert_called_with(
            'https://test',
            headers={
                **DEFAULT_HEADERS,
                'Accept': 'application/pdf',
            }
        )

    def test_get_request_no_body(self, mock_step, mock_successful_response, mock_requests_get):
        request = Request(mock_step)
        del mock_successful_response.body
        assert not request.request_executed
        assert not request.response_succeeded
        assert request.execute()
        assert request.request_executed
        assert request.response_succeeded
        mock_requests_get.assert_called_with(
            'https://test',
            headers={
                **DEFAULT_HEADERS,
                'Accept': 'application/pdf',
            }
        )

    def test_post_request(self, mock_step, mock_successful_response, mock_requests_post):
        request = Request(mock_step)
        mock_step.step_method = 'POST'
        mock_step.step_body = {'a': 'A'}
        assert not request.request_executed
        assert not request.response_succeeded
        assert request.execute()
        assert request.request_executed
        assert request.response_succeeded
        mock_requests_post.assert_called_with(
            'https://test',
            headers={
                **DEFAULT_HEADERS,
                'Accept': 'application/pdf',
            },
            json={'a': 'A'}
        )

    def test_post_request_with_string_body(self, mock_step, mock_successful_response, mock_requests_post):
        request = Request(mock_step)
        mock_step.step_method = 'POST'
        mock_step.step_body = 'NOT A JSON BODY'
        assert not request.request_executed
        assert not request.response_succeeded
        assert request.execute()
        assert request.request_executed
        assert request.response_succeeded
        mock_requests_post.assert_called_with(
            'https://test',
            headers={
                **DEFAULT_HEADERS,
                'Accept': 'application/pdf',
            },
            data='NOT A JSON BODY'
        )
