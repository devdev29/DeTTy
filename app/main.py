import socket  # noqa: F401
import os
import sys

from http_request import HttpRequest
from http_response import HttpResponse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    valid_targets = ['/']
    
    # Uncomment this to pass the first stage
    server_socket = create_server(address=("127.0.0.1", 4221), reuse_port=True)
    request_string = server_socket.accept()[0].recv(1024).decode()
    incoming_request =  HttpRequest(request_string=request_string)# wait for client
    target_resource = incoming_request.request_line['resource']
    if target_resource not in valid_targets:
        response = str(HttpResponse(status_code='404', reason_phrase='Not Found')).encode('ASCII')
        server_socket.accept()[0].send(response)
    else:
        response = str(HttpResponse(status_code='200',reason_phrase='OK'))
        server_socket.accept()[0].send(response)


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
