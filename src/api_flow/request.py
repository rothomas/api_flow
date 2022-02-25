import json
import requests
from api_flow.complex_namespace import ComplexNamespace


DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'api_flow/0.5',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}


class Request:
    @staticmethod
    def _format_body(body):
        if body is None:
            return ''
        elif isinstance(body, str):
            return body
        elif isinstance(body, ComplexNamespace):
            return json.dumps(body.as_dict(), indent=2)
        else:
            return json.dumps(body, indent=2)

    @staticmethod
    def _format_headers(headers):
        if headers is not None:
            output_headers = '\n'.join(list(map(lambda pair: f"{pair[0]}: {pair[1]}", headers.items())))
            return f"{output_headers}\n\n"
        return ''

    def __init__(self, step):
        self.request_step = step
        self.response = None

    def _get_response_body(self):
        if self.response is not None and hasattr(self.response, 'text'):
            body = self.response.text
            if isinstance(body, str) and len(body) > 0:
                try:
                    body = json.loads(body)
                except ValueError:
                    pass
                return body
        return ''

    def _log_request(self):
        print('vvvvvvvvvvvvvvvvvvv')
        print('===== REQUEST =====')
        print(f'{self.request_step.step_method.upper()} {self.request_step.step_url}')
        print(self._format_headers(self.request_headers))
        print(self._format_body(self.request_step.step_body))

    def _log_response(self):
        print('===== RESPONSE =====')
        print(f'HTTP {self.response.status_code}')
        print(self._format_headers(self.response.headers))
        print(self._format_body(self.response_body))
        print("^^^^^^^^^^^^^^^^^^^^")

    def _make_request(self):
        body = self.request_step.step_body
        headers = self.request_headers
        url = self.request_step.step_url
        if body is None:
            return self.request_method(url, headers=headers)
        elif isinstance(body, str):
            return self.request_method(url, headers=headers, data=body)
        else:
            if isinstance(body, ComplexNamespace):
                body = body.as_dict()
            return self.request_method(url, headers=headers, json=body)

    def execute(self):
        self._log_request()
        self.response = self._make_request()
        self._log_response()
        return self.response_succeeded

    request_executed = property(
        lambda self: self.response is not None
    )
    request_method = property(
        lambda self: getattr(requests, self.request_step.step_method.lower())
    )
    request_headers = property(
        lambda self: {
            **DEFAULT_HEADERS,
            **self.request_step.step_headers
        }
    )
    response_body = property(_get_response_body)
    response_status_code = property(
        lambda self:
            self.response.status_code if self.request_executed else None
    )
    response_succeeded = property(
        lambda self: self.request_executed and self.response.ok
    )
