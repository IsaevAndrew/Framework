import mimetypes
import threading
import socket
from router import Router
import os


class SimpleFramework:
    def __init__(self, static_folder="static", template_folder="templates"):
        self.routes = Router()
        self.static_folder = static_folder
        self.template_folder = template_folder

    def route(self, path, methods=["GET"]):
        """ Регистрация маршрута для конкретного пути """

        def wrapper(func):
            self.routes[(path, tuple(methods))] = func
            return func

        return wrapper

    def get_route(self, path, method):
        """ Получаем обработчик для маршрута по пути и методу """
        for (route_path, methods), func in self.routes.items():
            if path == route_path and method in methods:
                return func
        return None

    def render_template(self, template_name, context=None):
        """ Простая шаблонизация """
        if context is None:
            context = {}
        template_path = os.path.join("templates", template_name)
        with open(template_path, "r") as f:
            template = f.read()

        # Заменяем переменные в шаблоне на значения из context
        for key, value in context.items():
            template = template.replace(f"{{{{ {key} }}}}", str(value))

        return template

    def handle_request(self, request):
        lines = request.split("\r\n")
        method, path, _ = lines[0].split(" ")
        if path.startswith("/static/"):
            return self.serve_static_file(path)

        handler = self.get_route(path, method)
        if handler:
            try:
                response_body = handler(self)
                return self.build_response("200 OK", "text/html", response_body)
            except Exception as e:
                return self.handle_error(e)
        else:
            return self.build_response("404 Not Found", "text/html",
                                       "<h1>404 Not Found</h1>")

    def build_response(self, status, content_type, body):
        return f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\n\r\n{body}"

    def serve_static_file(self, path):
        file_path = os.path.join(self.static_folder, path[len("/static/"):])
        if os.path.exists(file_path) and os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            with open(file_path, "rb") as f:
                content = f.read()
            return self.build_response("200 OK", mime_type, content)
        return self.build_response("404 Not Found", "text/html",
                                   "<h1>404 Not Found</h1>")

    def handle_error(self, error):
        return self.build_response("500 Internal Server Error", "text/html",
                                   f"<h1>500 Internal Server Error: {str(error)}</h1>")

    def __call__(self, environ, start_response):
        """ Обработка входящих WSGI-запросов """
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")
        handler = self.get_route(path, method)

        if handler:
            response_body = handler(self)
            start_response("200 OK", [("Content-Type", "text/html")])
        else:
            response_body = "<h1>404 Not Found</h1>"
            start_response("404 Not Found", [("Content-Type", "text/html")])

        return [response_body.encode("utf-8")]

    def start_server(self, host="127.0.0.1", port=8080):
        """ Запуск сервера с использованием многопоточности """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)

        print(f"Server started at http://{host}:{port}")

        def handle_client(client_socket):
            try:
                request = client_socket.recv(1024).decode()
                if request:
                    response = self.handle_request(request)
                    client_socket.sendall(response.encode())
            except Exception as e:
                print(f"Error handling client: {e}")
            finally:
                client_socket.close()

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection established with {client_address}")
            client_thread = threading.Thread(target=handle_client,
                                             args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
