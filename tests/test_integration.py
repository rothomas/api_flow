import json
import os
import pytest
import threading
from api_flow import execute, configure
from api_flow.complex_namespace import ComplexNamespace
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest.mock import MagicMock

response_success_json = ComplexNamespace(
    status_code=200,
    headers={
        'Content-Type': 'application/json'
    },
    body=json.dumps({"id": "123abc"})
)

response_success_plain = ComplexNamespace(
    status_code=200,
    headers={
        'Content-Type': 'text/plain'
    },
    body='THIS IS THE RESPONSE'
)

response_fail_json = ComplexNamespace(
    status_code=400,
    headers={
        'Content-Type': 'application/json'
    },
    body=json.dumps({"id": "123abc"})
)


@pytest.fixture
def http_response_factory():
    http_response_factory = MagicMock()
    http_response_factory.return_value = response_success_json
    yield http_response_factory


@pytest.fixture
def http_handler(http_response_factory):
    class HTTPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            response = http_response_factory(self)
            self.send_response(response.status_code)
            for item in response.headers.items():
                self.send_header(*item)
            self.end_headers()
            self.wfile.write(response.body.encode("utf-8"))

        def do_POST(self):
            return self.do_GET()

    yield HTTPHandler


@pytest.fixture()
def httpd(http_handler):
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), http_handler)
    threading.Thread(name='test_http_server',
                     target=lambda: httpd.serve_forever()).start()
    yield httpd
    httpd.shutdown()


@pytest.fixture(autouse=True)
def setup():
    configure(
        data_path=os.path.join(os.path.dirname(__file__), 'test_data'),
        profile_path=None,
        flow_path=None,
        function_path=None,
        template_path=None
    )


class TestIntegration:
    def test_prerequisite_only(self, httpd, http_response_factory):
        flow = execute('prerequisite_flow', server_port=httpd.server_port)
        assert flow.prerequisite_step.id == '123abc'

    def test_prerequisite_non_json_response_body(self, httpd, http_response_factory):
        http_response_factory.return_value = response_success_plain
        flow = execute('prerequisite_flow', server_port=httpd.server_port)
        assert flow.prerequisite_step.step_request.response_body == 'THIS IS THE RESPONSE'

    def test_flow_with_prerequisite(self, httpd, http_response_factory):
        flow = execute('has_prerequisite', server_port=httpd.server_port)
        assert flow.prerequisite_flow.prerequisite_step.id == '123abc'

    def test_flow_with_profile(self, httpd, http_response_factory):
        flow = execute('profile_sub', profile='foo', profiles=['bar', 'baz'], server_port=httpd.server_port)
        assert flow.substitute.step_url.endswith('/Foo/Bar/Baz')

    def test_flow_with_environment_sub(self, httpd, http_response_factory):
        os.environ['foo'] = 'FOO'
        os.environ['bar'] = 'BAR'
        os.environ['baz'] = 'BAZ'
        flow = execute('profile_sub', server_port=httpd.server_port)
        assert flow.substitute.step_url.endswith('/FOO/BAR/BAZ')
        del os.environ['foo']
        del os.environ['bar']
        del os.environ['baz']

    def test_function_substitution(self, httpd, http_response_factory):
        flow = execute('function_sub', server_port=httpd.server_port)
        assert flow.first.step_url.endswith('/EchoTest')

    def test_post_requests(self, httpd, http_response_factory):
        flow = execute('post_requests', server_port=httpd.server_port)

    def test_failed_flow(self, httpd, http_response_factory):
        http_response_factory.return_value = response_fail_json
        flow = execute('prerequisite_flow', server_port=httpd.server_port)
        assert not flow.succeeded

    def test_empty_flow(self, httpd, http_response_factory):
        flow = execute('empty', server_port=httpd.server_port)
        assert flow.succeeded
