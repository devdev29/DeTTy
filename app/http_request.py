from app.exceptions import NoHeadersFoundError, InvalidBodyError 

class HttpRequest:
    def __init__(self, method, path_info, query_string, http_version, request_headers, request_body):
       self.method = method
       self.path_info = path_info
       self.query_string = query_string
       self.http_version = http_version
       self.request_headers = request_headers
       self.request_body = request_body
    
    @classmethod
    def from_http_string(cls, request_string: str):
        request_list = request_string.split('\r\n')
        method, path_info, query_string, http_version = cls._extract_request_line(request_list)
        request_headers = cls._extract_request_headers(request_list)
        request_body = request_list[-1]
        return cls(method, path_info, query_string, http_version, request_headers, request_body) 

    @classmethod
    def from_wsgi_environ(cls, environ: dict):
        method = environ['REQUEST_METHOD']
        path_info = environ['PATH_INFO']
        query_string = environ['QUERY_STRING']
        http_version = environ.get('SERVER_PROTOCOL', 'HTTP/1.1')
        request_headers = cls._extract_headers_from_environ(environ)
        request_body = cls._read_body_from_environ(environ)
        return cls(method, path_info, query_string, http_version, request_headers, request_body)

    @staticmethod
    def _extract_headers_from_environ(environ: dict) -> dict[str, str]:
        """Extract HTTP headers from WSGI environ dict."""
        headers = {}
        
        # Add Content-Type and Content-Length if present
        if 'CONTENT_TYPE' in environ:
            headers['Content-Type'] = environ['CONTENT_TYPE']
        if 'CONTENT_LENGTH' in environ and environ['CONTENT_LENGTH']:
            headers['Content-Length'] = environ['CONTENT_LENGTH']
        
        # Extract HTTP_* headers
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                # Convert HTTP_USER_AGENT to User-Agent
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        
        return headers
    
    @staticmethod
    def _read_body_from_environ(environ: dict) -> str:
        """Read request body from WSGI environ."""
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            content_length = 0
        
        if content_length > 0:
            body = environ['wsgi.input'].read(content_length)
            if isinstance(body, bytes):
                return body.decode('utf-8')
            return body
        return ''

    @staticmethod
    def _extract_request_line(request_list: list):
        request_line = request_list[0]
        request_components = request_line.split(' ')
        if len(request_components) != 3:
            raise InvalidBodyError('Invalid HTTP request format')
        method = request_components[0]
        resource = request_components[1]
        if '?' in resource:
            path_info, query_string = resource.split('?', 1)
        else:
            path_info = resource
            query_string = ''
        http_version = request_components[2]
        return method, path_info, query_string, http_version

    @staticmethod
    def _extract_request_headers(request_list: list):
        request_headers_raw = request_list[1:-2]
        request_headers = {}
        if not request_headers_raw:
                raise NoHeadersFoundError('No HTTP headers found, you must specify at least Host for this to be a valid HTTP request')
        for raw_header in request_headers_raw:
            header, value = raw_header.split(':',1)
            request_headers.update({header: value.lstrip()})
        return request_headers
    
    def extract_query_parameters(self):
        query_parameter_values = {}
        if self.query_string:
            if '&' not in self.query_string:
                if '=' not in self.query_string:
                    raise InvalidBodyError('Invalid HTTP request format')
                query_parameter_values.update({self.query_string.split('=')[0]: self.query_string.split('=')[1]})
            else:
                query_parameter_list = self.query_string.split('&')
                for query_parameter in query_parameter_list:
                    if '=' not in query_parameter:
                        raise InvalidBodyError('Invalid HTTP request format')
                    query_parameter_values.update({query_parameter.split('=')[0]: query_parameter.split('=')[1]})
        return query_parameter_values
    
    def extract_accept_encodings(self):
        accept_encoding = self.request_headers.get('Accept-Encoding', '')
        client_encodings = [
        enc.split(';')[0].strip() 
        for enc in accept_encoding.split(',')]
        return client_encodings
