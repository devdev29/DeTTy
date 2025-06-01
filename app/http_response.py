from dataclasses import dataclass,field

@dataclass
class HttpResponse:
    status_code: str
    reason_phrase: str
    http_version: str = "HTTP/1.1"
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: str = ''

    def __str__(self):
        status_line = f'{self.http_version} {self.status_code} {self.reason_phrase}\r\n'
        http_response_string = status_line
        if self.response_headers:
            for header, value in self.response_headers:
                response_header = f'{header}: {value}\r\n'
                http_response_string+=response_header
        else:
            http_response_string+='\r\n'
        if self.response_body:
            http_response_string+=f'{self.response_body}\r\n'
        return http_response_string
