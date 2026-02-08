"""
WSGI adapter for DeTTy framework.
Implements the WSGI application interface (PEP 3333).
"""

import traceback
from typing import Callable, Iterable

from app.application import Application
from app.http_request import HttpRequest


class WSGIApplication:
    """
    WSGI application adapter.
    
    Wraps a DeTTy Application instance and exposes it as a WSGI callable.
    """
    
    def __init__(self, application: Application):
        """
        Initialize WSGI application.
        
        Args:
            application: DeTTy Application instance
        """
        self.application = application
    
    def __call__(
        self, 
        environ: dict, 
        start_response: Callable[[str, list[tuple[str, str]]], None]
    ) -> Iterable[bytes]:
        """
        WSGI application callable.
        
        Args:
            environ: WSGI environment dictionary
            start_response: WSGI start_response callable
        
        Returns:
            Iterable of bytes (response body)
        """
        try:
            # Convert WSGI environ to HttpRequest
            request = HttpRequest.from_wsgi_environ(environ)
            
            # Handle request using core application logic
            response = self.application.handle_request(request)
            
            # Convert HttpResponse to WSGI format
            status, headers, body = response.to_wsgi_response()
            
            # Call start_response
            start_response(status, headers)
            
            # Return iterable of body bytes
            return [body]
            
        except Exception as e:
            # Error handling - catch any uncaught exceptions
            traceback.print_exc()
            error_response = self.application.get_error_response(e)
            status, headers, body = error_response.to_wsgi_response()
            start_response(status, headers)
            return [body]
