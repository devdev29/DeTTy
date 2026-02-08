"""
Core application logic for DeTTy framework.
Separated from server/socket concerns for WSGI compliance.
"""

from typing import Any
import traceback

from pydantic import BaseModel

from app.path_registry import PathRegistry
from app.http_request import HttpRequest
from app.http_response import HttpResponse
from app.http_constants import HttpStatus, DEFAULT_METHOD_STATUS
from app.exceptions import ExternalError
from app.models import FunctionParameters


class Application:
    """Core framework application logic without server/socket handling."""
    
    def __init__(self) -> None:
        self.path_registry = PathRegistry()
    
    def register(self, path_string: str, method: str, override: bool = False):
        """
        Decorator function for registering routes.
        
        Usage:
            @app.register('/echo/{message}', 'GET')
            def echo(message: str):
                return message
        """
        def decorator(func):
            self.path_registry.add_route(
                path_string=path_string,
                method=method,
                func=func,
                override=override
            )
            return func
        return decorator
    
    def get_default_http_response(self, request_method: str) -> HttpResponse:
        """Get default HTTP response based on request method."""
        status = DEFAULT_METHOD_STATUS.get(request_method, HttpStatus.METHOD_NOT_ALLOWED)
        return HttpResponse(status_code=status.code, reason_phrase=status.phrase)
    
    def get_error_response(self, error: ExternalError | Exception) -> HttpResponse:
        """Convert an exception to an HTTP error response."""
        if isinstance(error, ExternalError):
            return HttpResponse(status_code=error.code, reason_phrase=error.reason_phrase)
        else:
            return HttpResponse(
                HttpStatus.INTERNAL_SERVER_ERROR.code, 
                HttpStatus.INTERNAL_SERVER_ERROR.phrase
            )
    
    def _infer_media_type(self, response_body) -> str:
        """Infer Content-Type based on response body type."""
        if isinstance(response_body, str):
            return 'text/plain'
        elif isinstance(response_body, (dict, list, BaseModel)):
            return 'application/json'
        elif isinstance(response_body, bytes):
            return 'application/octet-stream'
        return 'text/plain'
    
    def solve_values(
        self, 
        request: HttpRequest, 
        field_info: FunctionParameters, 
        request_path_params: dict[str, str], 
        response_object: HttpResponse
    ) -> dict[str, Any]:
        """
        Resolve all parameter values for a route handler.
        Extracts and validates path, query, header, and body parameters.
        """
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
        
        # Inject response object if handler requested it
        if field_info.response_argument:
            values[field_info.response_argument] = response_object
        
        return values
    
    def handle_request(self, request: HttpRequest) -> HttpResponse:
        """
        Core request handling logic.
        Routes request to appropriate handler and builds response.
        """
        try:
            # Create default response for this HTTP method
            response = self.get_default_http_response(request.method)
            
            # Match route and get handler function
            func, field_info, path_params = self.path_registry.match(
                request.path_info,
                request.method
            )
            
            # Resolve all parameters for the handler
            values = self.solve_values(request, field_info, path_params, response)
            
            # Execute handler
            solved = func(**values)
            
            # Build response
            if isinstance(solved, HttpResponse):
                response = solved
            else:
                response_body = solved if solved is not None else ''
                response.response_body = response_body
                response.media_type = self._infer_media_type(response_body)
            
            # Apply compression if client supports it
            response.compress_body(request.extract_accept_encodings())
            
            return response
            
        except Exception as e:
            traceback.print_exc()
            return self.get_error_response(e)

