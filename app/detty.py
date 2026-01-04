import socket
import os

from typing import Any

from app.path_registry import PathRegistry
from app.http_request import HttpRequest
from app.http_response import HttpResponse
from app.http_constants import HttpStatus
from app.exceptions import ExternalError
from app.models import FunctionParameters

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

    def handle_request(self, server_socket: socket.socket) -> HttpResponse:
        connection = server_socket.accept()[0]
        incoming_request = connection.recv(1024).decode()
        request = HttpRequest(incoming_request)
        try:
            func, field_info, path_params = self.path_registry.match(request.resource, request.method)
            values = self.solve_values(request, field_info, path_params)
            solved = func(**values)
            response_body = solved #add logic to convert objects to json strings
            success_resp= str(HttpResponse(status_code=HttpStatus.OK.code, reason_phrase=HttpStatus.OK.phrase, response_body=response_body)).encode('ASCII')# Add request evaluation code here
            connection.send(success_resp)
        except Exception as e:
            print(e.with_traceback()) #TODO: replace with proper error logging later
            error_resp = str(self.get_error_response(e)).encode('ASCII')
            connection.send(error_resp)
        finally:
            connection.close()
        
    def run(self):
        server = self.create_server(address=("127.0.0.1", 4221), reuse_port=False)
        self.handle_request(server)
    
    def solve_values(self, request: HttpRequest, field_info: FunctionParameters, request_path_params: dict[str, str]) -> dict[str, Any]:
        values = {}
        print(request)
        request_body = request.request_body
        request_query_params = request.extract_query_parameters()
        request_headers = request.request_headers

        for param_name, param in field_info.path_arguments.items():
            raw_path_value = request_path_params.get(param_name)
            path_value = param.validate_value(raw_path_value)
            values[param_name] = path_value
        for param_name, param in field_info.query_arguments.items():
            if param_name in request_query_params:
                raw_query_value = request_query_params.get(param_name)
                query_value = param.validate_value(raw_query_value)
                values[param_name] = query_value
            else:
                #just populate the default value
                values[param_name] = param.default_value
        for param_name, header in field_info.header_arguments.items():
            if header.header_name in request_headers:
                raw_header_value = request_headers.get(header.header_name)
                header_value = header.validate_value(raw_header_value)
                values[param_name] = header_value
            else:
                values[param_name] = param.default_value
        for param_name, body in field_info.body_arguments.items():
            body_value = body.validate_value(request_body)
            values[param_name] = body_value
        
        return values
