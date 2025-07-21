from dataclasses import dataclass,field
from typing import Any

@dataclass
class HttpResponse:
    status_code: str
    reason_phrase: str
    http_version: str = 'HTTP/1.1'
    response_headers: dict[str, str] = field(default_factory=dict)
    media_type: str = 'text/plain; charset=utf-8'
    response_body: Any = ''

    def __str__(self):
        status_line = f'{self.http_version} {self.status_code} {self.reason_phrase}\r\n'
        http_response_string = status_line
        self.response_headers['Content-Type']=self.media_type
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
    
    def __repr__(self):
        return str(self)
