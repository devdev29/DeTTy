from typing import Callable
from wsgiref.simple_server import make_server, WSGIRequestHandler
import click

from app.application import Application
from app.wsgi import WSGIApplication


class QuietWSGIRequestHandler(WSGIRequestHandler):
    """Custom WSGI request handler with optional logging."""
    
    def log_message(self, format, *args):
        if hasattr(self.server, 'verbose') and self.server.verbose:
            super().log_message(format, *args)


class DeTTy:
    """
    Main DeTTy framework class.
    
    This class is WSGI-callable and can be used directly with any WSGI server.
    
    Example:
        app = DeTTy()
        
        @app.register('/', 'GET')
        def home():
            return "Hello, World!"
        
        # For WSGI servers (production)
        # gunicorn app.main:app
    """
    
    def __init__(self) -> None:
        """Initialize DeTTy application."""
        self.application = Application()
        self._wsgi_app = None
    
    def register(self, path_string: str, method: str, override: bool = False):
        """
        Decorator function for registering routes.
        
        Args:
            path_string: URL path pattern (e.g., '/users/{id}')
            method: HTTP method (e.g., 'GET', 'POST')
            override: Whether to override existing route
        
        Usage:
            @app.register('/echo/{message}', 'GET')
            def echo(message: str):
                return message
        """
        return self.application.register(path_string, method, override)
    
    @property
    def wsgi_app(self) -> WSGIApplication:
        """
        Get WSGI application callable.
        
        Returns:
            WSGIApplication instance
        """
        if self._wsgi_app is None:
            self._wsgi_app = WSGIApplication(self.application)
        return self._wsgi_app
    
    def __call__(self, environ: dict, start_response: Callable) -> list[bytes]:
        """
        Make DeTTy itself WSGI callable.
        
        This allows the DeTTy instance to be used directly with WSGI servers.
        
        Args:
            environ: WSGI environment dict
            start_response: WSGI start_response callable
        
        Returns:
            Response body as list of bytes
        """
        return self.wsgi_app(environ, start_response)
    
    def run(
        self, 
        host: str = '127.0.0.1', 
        port: int = 4221, 
        verbose: bool = True
    ):
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
        click.echo(f"Running on http://{host}:{port}")
        click.echo("Press CTRL+C to quit")
        click.echo()
        
        with make_server(
            host, 
            port, 
            self.wsgi_app,
            handler_class=QuietWSGIRequestHandler
        ) as server:
            server.verbose = verbose
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                click.echo()
                click.echo(click.style('\nSHUTTING DOWN: User keyboard interrupt detected', fg='red'))
