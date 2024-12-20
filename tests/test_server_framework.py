import threading
import unittest
from unittest.mock import MagicMock, patch
from response import Response, HtmlResponse, JsonResponse, TextResponse
from server import SimpleFramework


class TestSimpleFramework(unittest.TestCase):
    def setUp(self):
        self.app = SimpleFramework()

    # Тесты ответов
    def test_html_response(self):
        """Тест HTML ответа"""
        response = HtmlResponse("<h1>Hello</h1>")
        http_response = response.to_http_response()
        self.assertIn(b"200 OK", http_response)
        self.assertIn(b"text/html", http_response)
        self.assertIn(b"<h1>Hello</h1>", http_response)

    def test_json_response(self):
        """Тест JSON ответа"""
        response = JsonResponse({"key": "value"})
        http_response = response.to_http_response()
        self.assertIn(b"200 OK", http_response)
        self.assertIn(b"application/json", http_response)
        self.assertIn(b'{"key": "value"}', http_response)

    def test_text_response(self):
        """Тест текстового ответа"""
        response = TextResponse("Simple text")
        http_response = response.to_http_response()
        self.assertIn(b"200 OK", http_response)
        self.assertIn(b"text/plain", http_response)
        self.assertIn(b"Simple text", http_response)

    def test_500_response_on_error(self):
        """Тест генерации 500 при ошибке"""
        with self.assertRaises(ValueError):
            raise ValueError("Test Error")

    def test_static_file_not_found(self):
        """Тест отсутствующего статического файла"""
        with patch("os.path.exists", MagicMock(return_value=False)):
            response = self.app.serve_static_file("/static/missing.txt")
            self.assertIn("404 Not Found", response)

    # Тесты обработки ошибок
    def test_handle_error(self):
        """Тест обработки ошибок"""
        response = self.app.handle_error(Exception("Error message"))
        self.assertIn("500 Internal Server Error", response)
        self.assertIn("Error message", response)

    # Тесты обработки клиента
    def test_handle_client(self):
        """Тест обработки клиентских запросов"""
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"

        @self.app.route("/", methods=["GET"])
        def index(_):
            return HtmlResponse("<h1>Hello, World!</h1>")

        self.app.handle_client(mock_socket)
        mock_socket.sendall.assert_called_once()
        response = mock_socket.sendall.call_args[0][0]
        self.assertIn(b"200 OK", response)
        self.assertIn(b"Hello, World!", response)

    def test_handle_client_error(self):
        """Тест обработки клиентских ошибок"""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = Exception("Client error")
        self.app.handle_client(mock_socket)
        mock_socket.sendall.assert_called()

    def test_worker(self):
        """Тест рабочего потока"""
        mock_socket = MagicMock()
        self.app.task_queue.put(mock_socket)
        thread = threading.Thread(target=self.app.worker, daemon=True)
        thread.start()
        self.app.task_queue.put(None)  # Завершение потока
        thread.join()
        mock_socket.close.assert_called()

    def test_middleware(self):
        """Тест добавления и использования middleware"""

        def test_middleware(environ):
            environ["test_key"] = "test_value"
            return environ

        self.app.use(test_middleware)
        self.assertIn(test_middleware, self.app.middleware)


if __name__ == "__main__":
    unittest.main()
