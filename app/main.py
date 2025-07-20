import socket  # noqa: F401
import os
import sys

from http_request import HttpRequest
from http_response import HttpResponse
from http_constants import HttpStatusCodes, HttpReasonPhrases
from path_registry import PathRegistry

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

pr = PathRegistry()

@pr.register('/', 'GET')
def empty_func():
    ...

@pr.register('/echo/{in_str}', 'GET')
def echo(in_str: str):
    return in_str

def main():
    server_socket = create_server(address=("127.0.0.1", 4221), reuse_port=False)
    connection = server_socket.accept()[0]
    
    request_string = connection.recv(1024).decode()
    incoming_request =  HttpRequest(request_string=request_string)# wait for client
    target_resource = incoming_request.resource
    method = incoming_request.method
    
    try:
        result = pr.evaluate(target_resource, method)
        if result:
            response = str(HttpResponse(status_code=HttpStatusCodes.OK, reason_phrase=HttpReasonPhrases.OK, response_body=result)).encode('ASCII')
        else:
            response = str(HttpResponse(status_code=HttpStatusCodes.OK, reason_phrase=HttpReasonPhrases.OK)).encode('ASCII')
    except Exception as e:
        if hasattr(e, 'code'):
            response = str(HttpResponse(status_code=e.code, reason_phrase=e.reason_phrase)).encode('ASCII')
        else:
            response = str(HttpResponse(status_code=HttpStatusCodes.INTERNAL_SERVER_ERROR, reason_phrase=HttpReasonPhrases.INTERNAL_SERVER_ERROR)).encode('ASCII')
        print(e)

    connection.send(response)
    connection.close()

def create_server(address: tuple, reuse_port: bool = False, backlog: int|None = None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if os.name not in ('nt', 'cygwin'):
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if reuse_port:
        try:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            raise ValueError("SO_REUSEPORT not supported on this platform")
    server_socket.bind(address)
    if backlog:
        server_socket.listen(backlog)
    else:
        server_socket.listen()
    return server_socket

if __name__ == "__main__":
    main()
