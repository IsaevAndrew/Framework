import unittest
from response import Response, JsonResponse, HtmlResponse, TextResponse


class TestResponse(unittest.TestCase):
    # Тесты для базового класса Response
    def test_response_initialization(self):
        """Тест корректной инициализации Response"""
        response = Response("<h1>Test</h1>")
        self.assertEqual(response.body, "<h1>Test</h1>")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "text/html")

    def test_response_to_http_response(self):
        """Тест преобразования Response в HTTP-ответ"""
        response = Response("<h1>Test</h1>")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: text/html", http_response)
        self.assertIn(b"<h1>Test</h1>", http_response)

    def test_response_with_bytes_body(self):
        """Тест Response с байтовым телом"""
        response = Response(b"binary data", content_type="application/octet-stream")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: application/octet-stream", http_response)
        self.assertIn(b"binary data", http_response)

    def test_response_empty_body(self):
        """Тест Response с пустым телом"""
        response = Response("")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: text/html", http_response)
        self.assertIn(b"Content-Length: 0", http_response)

    def test_response_custom_status_and_content_type(self):
        """Тест Response с нестандартным статусом и типом контента"""
        response = Response("<h1>Test</h1>", status="404 Not Found", content_type="application/xml")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 404 Not Found", http_response)
        self.assertIn(b"Content-Type: application/xml", http_response)

    def test_response_invalid_body_type(self):
        """Тест Response с некорректным типом тела"""
        with self.assertRaises(TypeError):
            Response(123)  # Тело не строка или байты

    # Тесты для JsonResponse
    def test_json_response(self):
        """Тест корректной работы JsonResponse"""
        data = {"key": "value", "status": "success"}
        response = JsonResponse(data)
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: application/json", http_response)
        self.assertIn(b'{"key": "value", "status": "success"}', http_response)

    def test_json_response_empty_data(self):
        """Тест JsonResponse с пустыми данными"""
        response = JsonResponse({})
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: application/json", http_response)
        self.assertIn(b"{}", http_response)

    def test_json_response_custom_status(self):
        """Тест JsonResponse с нестандартным статусом"""
        data = {"error": "not found"}
        response = JsonResponse(data, status="404 Not Found")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 404 Not Found", http_response)
        self.assertIn(b"Content-Type: application/json", http_response)
        self.assertIn(b'{"error": "not found"}', http_response)

    # Тесты для HtmlResponse
    def test_html_response(self):
        """Тест корректной работы HtmlResponse"""
        response = HtmlResponse("<h1>HTML Test</h1>")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: text/html", http_response)
        self.assertIn(b"<h1>HTML Test</h1>", http_response)

    def test_html_response_empty_body(self):
        """Тест HtmlResponse с пустым телом"""
        response = HtmlResponse("")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: text/html", http_response)
        self.assertIn(b"Content-Length: 0", http_response)

    def test_html_response_custom_status(self):
        """Тест HtmlResponse с нестандартным статусом"""
        response = HtmlResponse("<h1>Not Found</h1>", status="404 Not Found")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 404 Not Found", http_response)
        self.assertIn(b"Content-Type: text/html", http_response)
        self.assertIn(b"<h1>Not Found</h1>", http_response)

    # Тесты для TextResponse
    def test_text_response(self):
        """Тест корректной работы TextResponse"""
        response = TextResponse("Simple text response")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: text/plain", http_response)
        self.assertIn(b"Simple text response", http_response)

    def test_text_response_empty_body(self):
        """Тест TextResponse с пустым телом"""
        response = TextResponse("")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 200 OK", http_response)
        self.assertIn(b"Content-Type: text/plain", http_response)
        self.assertIn(b"Content-Length: 0", http_response)

    def test_text_response_custom_status(self):
        """Тест TextResponse с нестандартным статусом"""
        response = TextResponse("Not Found", status="404 Not Found")
        http_response = response.to_http_response()
        self.assertIn(b"HTTP/1.1 404 Not Found", http_response)
        self.assertIn(b"Content-Type: text/plain", http_response)
        self.assertIn(b"Not Found", http_response)


if __name__ == "__main__":
    unittest.main()
