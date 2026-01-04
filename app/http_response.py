import gzip

from dataclasses import dataclass,field
from typing import Any, Union

from app.http_constants import SUPPORTED_CONTENT_ENCODINGS

@dataclass
class HttpResponse:
    status_code: str
    reason_phrase: str
    http_version: str = 'HTTP/1.1'
    response_headers: dict[str, str] = field(default_factory=dict)
    media_type: str = 'text/plain'
    response_body: Union[str, Any] = ''

    def __bytes__(self) -> bytes:
        """Serialize the response to bytes for sending over socket."""
        # Get body as bytes
        if isinstance(self.response_body, bytes):
            body_bytes = self.response_body
        else:
            body_bytes = self.response_body.encode('ASCII')
        
        self.response_headers['Content-Type'] = self.media_type
        self.response_headers['Content-Length'] = len(body_bytes)
        
        # Build headers
        status_line = f'{self.http_version} {self.status_code} {self.reason_phrase}\r\n'
        headers = status_line
        for header, value in self.response_headers.items():
            headers += f'{header}: {value}\r\n'
        headers += '\r\n'
        
        return headers.encode('ASCII') + body_bytes + b'\r\n'

    def __str__(self):
        status_line = f'{self.http_version} {self.status_code} {self.reason_phrase}\r\n'
        http_response_string = status_line
        content_length = len(self.response_body.encode('ASCII'))
        
        self.response_headers['Content-Type']=self.media_type
        self.response_headers['Content-Length']=content_length
        if self.response_headers:
            for header, value in self.response_headers.items():
                response_header = f'{header}: {value}\r\n'
                http_response_string+=response_header
            http_response_string+='\r\n'
        else:
            http_response_string+='\r\n'
        if self.response_body:
            http_response_string+=f'{self.response_body}\r\n'
        return http_response_string
    
    def compress_body(self, compression_schemes: list[str]):
        compression_schemes = [scheme for scheme in compression_schemes if scheme in SUPPORTED_CONTENT_ENCODINGS]
        if self.response_body is not None and compression_schemes:
            self.response_body = gzip.compress(self.response_body.encode('ASCII'))
            self.response_headers['Content-Encoding'] = 'gzip'

    def __repr__(self):
        return str(self)
