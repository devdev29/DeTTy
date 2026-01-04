import socket
import os
import traceback

import click

from typing import Any
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel

from app.path_registry import PathRegistry
from app.http_request import HttpRequest
from app.http_response import HttpResponse
from app.http_constants import HttpStatus, DEFAULT_METHOD_STATUS
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

    def get_default_http_response(self, request_method: str) -> HttpResponse:
        status = DEFAULT_METHOD_STATUS.get(request_method, HttpStatus.METHOD_NOT_ALLOWED)
        return HttpResponse(status_code=status.code, reason_phrase=status.phrase)

    def handle_connection(self, connection: socket.socket) -> None:
        """Handle a single connection - can be run in a thread."""
        try:
            incoming_request = connection.recv(1024).decode()
            request = HttpRequest(incoming_request)
            response = self.get_default_http_response(request.method)
            func, field_info, path_params = self.path_registry.match(request.resource, request.method)
            values = self.solve_values(request, field_info, path_params, response)
            print(path_params)
            solved = func(**values)
            response_body = solved if solved is not None else ''
            if isinstance(solved, HttpResponse):
                response = solved
            else:
                response.response_body = response_body
                response.media_type = self._infer_media_type(response_body)
            connection.send(str(response).encode('ASCII'))
        except Exception as e:
            traceback.print_exc()
            error_resp = str(self.get_error_response(e)).encode('ASCII')
            connection.send(error_resp)
        finally:
            connection.close()

    def solve_values(self, request: HttpRequest, field_info: FunctionParameters, request_path_params: dict[str, str], response_object: HttpResponse) -> dict[str, Any]:
        values = {}
        query_params = request.extract_query_parameters()

        def resolve_param(param, source: dict) -> Any:
            """Resolve a parameter value from a source dict, falling back to default."""
            if param.request_key in source:
                return param.validate_value(source[param.request_key])
            return param.default_value

        # Path params are always required (no defaults)
        for param_name, param in field_info.path_arguments.items():
            values[param_name] = param.validate_value(request_path_params.get(param_name))

        # Query and header params use the same resolution logic
        for param_name, param in field_info.query_arguments.items():
            values[param_name] = resolve_param(param, query_params)

        for param_name, param in field_info.header_arguments.items():
            values[param_name] = resolve_param(param, request.request_headers)

        # Body params validate the entire request body
        for param_name, param in field_info.body_arguments.items():
            values[param_name] = param.validate_value(request.request_body)
        
        if field_info.response_argument:
            values[field_info.response_argument] = response_object
        
        return values

    def _infer_media_type(self, response_body):
        if isinstance(response_body, str):
            return 'text/plain'
        elif isinstance(response_body, (dict, list, BaseModel)):
            return 'application/json'
        elif isinstance(response_body, bytes):
            return 'application/octet-stream'

    def run(self, multithreaded: bool = False, max_workers: int = 5):
        server = self.create_server(address=("127.0.0.1", 4221), reuse_port=False)
        server.settimeout(1.0)  # Allow checking for KeyboardInterrupt
        click.clear()
        click.echo("-------------STARTING UP-----------------")
        click.echo(click.style('''
         /$$$$$$$         /$$$$$$$$ /$$$$$$$$       
        | $$__  $$       |__  $$__/|__  $$__/       
        | $$  \ $$  /$$$$$$ | $$      | $$ /$$   /$$
        | $$  | $$ /$$__  $$| $$      | $$| $$  | $$
        | $$  | $$| $$$$$$$$| $$      | $$| $$  | $$
        | $$  | $$| $$_____/| $$      | $$| $$  | $$
        | $$$$$$$/|  $$$$$$$| $$      | $$|  $$$$$$$
        |_______/  \_______/|__/      |__/ \____  $$
                                        /$$  | $$
                                        |  $$$$$$/
                                        \______/ 
        ''', fg='yellow'))
        
        executor = ThreadPoolExecutor(max_workers=max_workers) if multithreaded else None
        try:
            while True:
                try:
                    connection, _= server.accept()
                    if multithreaded:
                        executor.submit(self.handle_connection, connection)
                    else:
                        self.handle_connection(connection)
                except socket.timeout:
                    continue  # Check for KeyboardInterrupt
        except KeyboardInterrupt:
            click.echo(click.style('\nSHUTTING DOWN: User keyboard interrupt detected', fg='red'))
        finally:
            if executor:
                executor.shutdown(wait=False)
            server.close()
