class Request:
    def __init__(self, raw_request):
        self.method = None
        self.endpoint = None
        self.protocol = None
        self.headers = {}
        self.body = None
        self.parse_http_request(raw_request)

    def parse_http_request(self, request):
        split_request = request.split("\r\n")
        self.method, self.endpoint, self.protocol = split_request[0].split()

        headers = []
        for line in split_request[1:]:
            if line == "":
                break
            headers.append(line)

        for header in headers:
            key, value = header.split(": ", 1)
            self.headers[key] = value

        body_index = split_request.index("") + 1
        if body_index < len(split_request):
            self.body = "\r\n".join(split_request[body_index:])
        else:
            self.body = None

    def __repr__(self):
        return (
            f"Method: {self.method}\n"
            f"Endpoint: {self.endpoint}\n"
            f"Protocol: {self.protocol}\n"
            f"Headers: {self.headers}\n"
            f"Body: {self.body}"
        )
