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
        compression_type = compression_schemes[0] #any supported scheme will do
        if self.response_body is not None:
            # self.response_body = compress(self.response_body.encode('ASCII'))
            self.response_headers['Content-Encoding'] = compression_type

    def __repr__(self):
        return str(self)
