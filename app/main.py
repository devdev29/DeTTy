import socket  # noqa: F401
import os
import sys

from dataclasses import dataclass,field

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class HttpRequest:
    def __init__(self, request_string: str):
        request_list = request_string.split('\r\n')
        self.request_line = self.extract_request_line(request_list)
        self.request_headers = self.extract_request_headers(request_list)
        self.request_body = request_list[-1] 
    
    def extract_request_line(self, request_list: list):
        request_line = request_list[0]
        request_components = request_line.split(' ')
        if len(request_components) != 3:
            raise ValueError('Invalid HTTP request format')
        return {'method':request_components[0], 'resource':request_components[1], 'version':request_components[2]}

    def extract_request_headers(self, request_list: list):
        request_headers_raw = request_list[1:-2]
        request_headers = {}
        if not request_headers_raw:
                raise ValueError('No HTTP headers found, you must specify at least Host for this to be a valid HTTP request')
        for raw_header in request_headers_raw:
            header, value = raw_header.split(':',1)
            request_headers.update({header: value.lstrip()})

@dataclass
class HttpResponse:
    status_code: str
    reason_phrase: str
    http_version: str = "HTTP/1.1"
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: str = ''

    def __str__(self):
        status_line = f'{self.http_version} {self.status_code} {self.reason_phrase}\r\n'
        http_response_string = status_line
        if self.response_headers:
            for header, value in self.response_headers:
                response_header = f'{header}: {value}\r\n'
                http_response_string+=response_header
        else:
            http_response_string+='\r\n'
        if self.response_body:
            http_response_string+=f'{self.response_body}\r\n'
        return http_response_string

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    valid_targets = ['/']
    
    # Uncomment this to pass the first stage
    server_socket = create_server(address=("127.0.0.1", 4221), reuse_port=True)
    connection = server_socket.accept()[0]
    request_string = connection.recv(1024).decode()
    incoming_request =  HttpRequest(request_string=request_string)# wait for client
    target_resource = incoming_request.request_line['resource']
    if target_resource not in valid_targets:
        response = str(HttpResponse(status_code='404', reason_phrase='Not Found')).encode('ASCII')
        connection.send(response)
    else:
        response = str(HttpResponse(status_code='200',reason_phrase='OK')).encode('ASCII')
        connection.send(response)
    connection.close()


def create_server(address: tuple, reuse_port: bool = False, backlog: int|None = None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(address)
    if os.name not in ('nt', 'cygwin'):
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if reuse_port:
        try:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            raise ValueError("SO_REUSEPORT not supported on this platform")
    if backlog:
        server_socket.listen(backlog)
    else:
        server_socket.listen()
    return server_socket

if __name__ == "__main__":
    main()
