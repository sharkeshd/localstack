import http.server
import json
import socketserver
import threading

class ResponseMock:
    def __init__(self, http_endpoint: str):
        self.response: str = "response not set"
        self.http_endpoint = http_endpoint

    def set_reponse(self, response: str):
        self.response = response


class HTTPMockServer:
    def __init__(self, port: int, endpoint: str):
        self._port = port
        self._endpoint = endpoint
        self._httpd: socketserver.TCPServer | None = None
        self._server_thread: threading.Thread | None = None

        self.response_mock = ResponseMock(http_endpoint=f"http://{self._endpoint}:{self._port}")


    def __enter__(self) -> ResponseMock:
        response_mock = self.response_mock
        other = self

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == other._endpoint:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(response_mock.response.encode())
                    print(f"GET {self.path}: 200")
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"'{self.path}' Not found, try {other._endpoint} instead".encode("utf-8"))
                    print(f"GET {self.path}: 404")

            def do_POST(self) -> None:
                if self.path == other._endpoint:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(response_mock.response.encode())
                    print(f"POST {self.path}: 200")
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"'{self.path}' Not found, try {other._endpoint} instead".encode("utf-8"))
                    print(f"POST {self.path}: 404")


        self._httpd = socketserver.TCPServer(("", self._port), Handler)
        self._server_thread = threading.Thread(target=self._httpd.serve_forever)
        self._server_thread.start()

        return response_mock

    def __exit__(self, exctype, excinst, exctb):
        print('exit')
        if (self._httpd and self._server_thread):
            print('shutdown...')
            self._httpd.shutdown()
            self._server_thread.join()


