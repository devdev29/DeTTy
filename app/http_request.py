from typing import Any, Type
import orjson

from pydantic import BaseModel, ValidationError

from app.exceptions import NoHeadersFoundError, InvalidBodyError, UnexpectedBodyError

class HttpRequest:
    def __init__(self, request_string: str):
        request_list = request_string.split('\r\n')
        self.extract_request_line(request_list)
        self.request_headers = self.extract_request_headers(request_list)
        self.request_body = request_list[-1] 
    
    def extract_request_line(self, request_list: list):
        request_line = request_list[0]
        request_components = request_line.split(' ')
        if len(request_components) != 3:
            raise InvalidBodyError('Invalid HTTP request format')
        self.method = request_components[0]
        self.resource = request_components[1]
        self.http_version = request_components[2]

    def extract_request_headers(self, request_list: list):
        request_headers_raw = request_list[1:-2]
        request_headers = {}
        if not request_headers_raw:
                raise NoHeadersFoundError('No HTTP headers found, you must specify at least Host for this to be a valid HTTP request')
        for raw_header in request_headers_raw:
            header, value = raw_header.split(':',1)
            request_headers.update({header: value.lstrip()})

    def get_request_body_as_object(self, mapper:Type[Any]) -> Any:
        arg_dict = orjson.loads(self.request_body)
        try:
            request_body_object = mapper(**arg_dict)
            return request_body_object
        except ValidationError as ve:
            raise UnexpectedBodyError(self.request_body_object)  
    
