import json


class Response:
    def __init__(self, body, status="200 OK", content_type="text/html"):
        if not isinstance(body, (str, bytes)):
            raise TypeError("Body must be of type str or bytes")
        self.body = body
        self.status = status
        self.content_type = content_type

    def to_http_response(self):
        """ Формирует HTTP-ответ """
        if isinstance(self.body, str):
            body = self.body.encode("utf-8")
        else:
            body = self.body
        headers = f"HTTP/1.1 {self.status}\r\nContent-Type: {self.content_type}\r\nContent-Length: {len(body)}\r\n\r\n"
        return headers.encode("utf-8") + body


class JsonResponse(Response):
    def __init__(self, data, status="200 OK"):
        super().__init__(json.dumps(data), status,
                         content_type="application/json")


class HtmlResponse(Response):
    def __init__(self, html, status="200 OK"):
        super().__init__(html, status, content_type="text/html")


class TextResponse(Response):
    def __init__(self, text, status="200 OK"):
        super().__init__(text, status, content_type="text/plain")
