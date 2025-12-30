import socket
import os

from app.path_registry import PathRegistry
from app.http_request import HttpRequest
from app.http_response import HttpResponse
from app.http_constants import HttpStatus
from app.exceptions import ExternalError

class DeTTy:
    def __init__(self) -> None:
       self.path_registry = PathRegistry() 

    def register(self, path_string: str, method: str, override: bool = False):
        '''
        Decorator function for the internal add_route method to allow patterns like
        @app.register('/register/person/{id}', 'GET')
        def echo(id: str):
            return id
        '''
        def decorator(func):
            self.path_registry.add_route(
                path_string=path_string,
                method=method,
                func=func,
                override=override
            )
            return func
        return decorator

   #RUN METHODS 
    def create_server(self, address: tuple, reuse_port: bool = False, backlog: int|None = None):
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
    
    def get_error_response(self, error: ExternalError | Exception):
        if isinstance(error, ExternalError):
            return HttpResponse(status_code=error.code, reason_phrase=error.reason_phrase)
        else:
            return HttpResponse(HttpStatus.INTERNAL_SERVER_ERROR.code, HttpStatus.INTERNAL_SERVER_ERROR.phrase) 

    def handle_request(self, server_socket: socket.socket):
        connection = server_socket.accept()[0]
        incoming_request = connection.recv(1024).decode()
        request = HttpRequest(incoming_request)
        try:
            ... # Add request evaluation code here
        except Exception as e:
            print(e) #TODO: replace with proper error logging later
            error_resp = str(self.get_error_response(e)).encode('ASCII')
            connection.send(error_resp)
        finally:
            connection.close()
        
    def run(self):
        server = self.create_server(address=("127.0.0.1", 4221), reuse_port=False)
        self.handle_request(server)

