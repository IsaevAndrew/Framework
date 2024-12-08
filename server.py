import mimetypes
import threading
import socket

from request_ import Request
from response import Response
from router import Router
import os
import queue
import logging


class SimpleFramework:
    def __init__(self, static_folder="static", template_folder="templates",
                 max_threads=5):
        self.router = Router()
        self.static_folder = static_folder
        self.template_folder = template_folder
        self.task_queue = queue.Queue()
        self.max_threads = max_threads
        self.lock = threading.Lock()
        self.sessions = {}  # Хранение сессий
        self.middleware = []  # Список промежуточных обработчиков
        self.logger = self.setup_logging()

    def setup_logging(self):
        """ Настройка логирования """
        logger = logging.getLogger('SimpleFramework')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def route(self, path, methods=["GET"]):
        """Регистрация маршрута через маршрутизатор"""
        return self.router.route(path, methods)

    def render_template(self, template_name, context=None):
        """ Простая шаблонизация """
        try:
            if context is None:
                context = {}
            template_path = os.path.join(self.template_folder, template_name)
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template '{template_name}' not found")

            with open(template_path, "r") as f:
                template = f.read()

            # Заменяем переменные в шаблоне на значения из context
            for key, value in context.items():
                template = template.replace(f"{{{{ {key} }}}}", str(value))

            return template
        except Exception as e:
            self.logger.exception("Error rendering template")
            raise

    def handle_request(self, raw_request):
        try:
            request = Request(raw_request)
        except ValueError:
            self.logger.error("Invalid HTTP request format")
            return self.handle_error(Exception("Invalid HTTP request format"))

        try:
            if request.endpoint.startswith("/static/"):
                return self.serve_static_file(request.endpoint)

            environ = {"method": request.method, "path": request.endpoint}
            for mw in self.middleware:
                environ = mw(environ)

            handler, params = self.router.get_route(environ["path"],
                                                    environ["method"])
            if handler:
                response = handler(**params) if params else handler(self)

                if isinstance(response, Response):
                    return response.to_http_response()
                else:
                    raise ValueError(
                        "Handler did not return a valid Response object")
            else:
                return self.build_response("404 Not Found", "text/html",
                                           "<h1>404 Not Found</h1>")
        except Exception as e:
            self.logger.exception("Error during request handling")
            return self.handle_error(e)

    def build_response(self, status, content_type, body):
        return f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\n\r\n{body}"

    def serve_static_file(self, path):
        try:
            file_path = os.path.join(self.static_folder, path[len("/static/"):])
            if os.path.exists(file_path) and os.path.isfile(file_path):
                mime_type, _ = mimetypes.guess_type(file_path)
                mime_type = mime_type or "application/octet-stream"
                with open(file_path, "rb") as f:
                    content = f.read()
                return self.build_response("200 OK", mime_type, content)
            else:
                raise FileNotFoundError(f"Static file not found: {path}")
        except FileNotFoundError as e:
            self.logger.warning(str(e))
            return self.build_response("404 Not Found", "text/html",
                                       "<h1>404 Not Found</h1>")
        except Exception as e:
            self.logger.exception("Error serving static file")
            return self.handle_error(e)

    def handle_error(self, error):
        self.logger.exception("Internal Server Error")
        return self.build_response("500 Internal Server Error", "text/html",
                                   f"<h1>500 Internal Server Error: {str(error)}</h1>")

    def __call__(self, environ, start_response):
        """ Обработка входящих WSGI-запросов """
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")
        handler = self.router.get_route(path, method)

        if handler:
            response_body = handler(self)
            start_response("200 OK", [("Content-Type", "text/html")])
        else:
            response_body = "<h1>404 Not Found</h1>"
            start_response("404 Not Found", [("Content-Type", "text/html")])

        return [response_body.encode("utf-8")]

    def handle_client(self, client_socket):
        """ Обрабатываем запрос клиента в отдельном потоке """
        try:
            request = client_socket.recv(
                1024).decode()  # Декодируем входящий запрос
            if request:
                response = self.handle_request(request)
                if isinstance(response,
                              str):  # Если ответ в формате строки, преобразуем в байты
                    response = response.encode('utf-8')
                client_socket.sendall(response)  # Отправляем ответ
        except Exception as e:
            self.logger.exception("Error handling client request")
            try:
                error_response = self.handle_error(e).encode('utf-8')
                client_socket.sendall(error_response)
            except Exception:
                self.logger.error("Failed to send error response to client")
        finally:
            client_socket.close()

    def worker(self):
        """ Рабочий поток, который будет извлекать задачи из очереди и их обрабатывать """
        try:
            while True:
                client_socket = self.task_queue.get()
                if client_socket is None:
                    break  # Завершаем поток, если в очереди None
                self.handle_client(client_socket)
                self.task_queue.task_done()
        except Exception as e:
            self.logger.exception("Error in worker thread")

    def start_server(self, host="127.0.0.1", port=8080):
        """ Запуск сервера """
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(5)

            print(f"Server started at http://{host}:{port}")

            # Запускаем несколько рабочих потоков
            for _ in range(self.max_threads):
                threading.Thread(target=self.worker, daemon=True).start()

            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    self.logger.info(f"New connection from {client_address}")
                    # Помещаем клиентский сокет в очередь задач
                    self.task_queue.put(client_socket)
                except Exception as e:
                    self.logger.exception("Error accepting client connection")
        except Exception as e:
            self.logger.exception("Failed to start server")
            raise

    def use(self, middleware):
        """ Регистрация промежуточных обработчиков (middleware) """
        self.middleware.append(middleware)
