import re

class Router:
    def __init__(self):
        self.routes = {}

    def add_route(self, path: str, methods: list[str], func):
        route_key = (path, tuple(methods))
        if route_key in self.routes:
            raise ValueError(f"Route '{path}' with methods {methods} is already registered")
        self.routes[route_key] = func

    def get_route(self, path: str, method: str):
        for (route_path, methods), func in self.routes.items():
            if method not in methods:
                continue

            pattern = re.sub(r'<([^>]+)>', r'(?P<\1>[^/]+)', route_path)
            regex = f"^{pattern}$"

            match = re.match(regex, path)

            if match:
                # Получаем параметры из URL
                return func, match.groupdict()
        
        return None

    def route(self, path: str, methods: list[str] =["GET"]):
        """Декоратор для регистрации маршрута"""

        def wrapper(func):
            self.add_route(path, methods, func)
            return func

        return wrapper