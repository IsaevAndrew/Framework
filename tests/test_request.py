import unittest
from Framework.request import Request


class TestRequest(unittest.TestCase):
    def test_parse_http_request_get(self):
        raw_request = (
            "GET / HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "User-Agent: curl/7.68.0\r\n"
            "Accept: */*\r\n"
            "\r\n"
        )
        request = Request(raw_request)

        self.assertEqual(request.method, "GET")
        self.assertEqual(request.endpoint, "/")
        self.assertEqual(request.protocol, "HTTP/1.1")
        self.assertEqual(request.headers["Host"], "localhost")
        self.assertEqual(request.headers["User-Agent"], "curl/7.68.0")
        self.assertEqual(request.headers["Accept"], "*/*")
        self.assertEqual(request.body, "")

    def test_parse_http_request_post(self):
        raw_request = (
            "POST /submit HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "User-Agent: curl/7.68.0\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            "Content-Length: 27\r\n"
            "\r\n"
            "field1=value1&field2=value2"
        )
        request = Request(raw_request)

        self.assertEqual(request.method, "POST")
        self.assertEqual(request.endpoint, "/submit")
        self.assertEqual(request.protocol, "HTTP/1.1")
        self.assertEqual(request.headers["Host"], "localhost")
        self.assertEqual(request.headers["User-Agent"], "curl/7.68.0")
        self.assertEqual(
            request.headers["Content-Type"], "application/x-www-form-urlencoded"
        )
        self.assertEqual(request.headers["Content-Length"], "27")
        self.assertEqual(request.body, "field1=value1&field2=value2")

    def test_parse_http_request_no_headers(self):
        raw_request = "GET / HTTP/1.1\r\n" "\r\n"
        request = Request(raw_request)

        self.assertEqual(request.method, "GET")
        self.assertEqual(request.endpoint, "/")
        self.assertEqual(request.protocol, "HTTP/1.1")
        self.assertEqual(request.headers, {})
        self.assertEqual(request.body, "")

    def test_parse_http_request_empty_body(self):
        raw_request = (
            "POST /submit HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            "Content-Length: 0\r\n"
            "\r\n"
        )
        request = Request(raw_request)

        self.assertEqual(request.method, "POST")
        self.assertEqual(request.endpoint, "/submit")
        self.assertEqual(request.protocol, "HTTP/1.1")
        self.assertEqual(request.headers["Host"], "localhost")
        self.assertEqual(
            request.headers["Content-Type"], "application/x-www-form-urlencoded"
        )
        self.assertEqual(request.headers["Content-Length"], "0")
        self.assertEqual(request.body, "")
