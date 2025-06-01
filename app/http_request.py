
class HttpRequest:
    def __init__(self, request_string: str):
        request_list = request_string.split('\r\n')
        self.request_line = self.extract_request_line(request_list)
        self.request_headers = self.extract_request_headers(request_list)
        self.request_body = request_list[-1] 
    
    def extract_request_line(self, request_list: list):
        request_line = request_list[0]
        request_components = request_line.split(' ')
        if len(request_components) != 3:
            raise ValueError('Invalid HTTP request format')
        return {'method':request_components[0], 'resource':request_components[1], 'version':request_components[2]}

    def extract_request_headers(self, request_list: list):
        request_headers_raw = request_list[1:-2]
        request_headers = {}
        if not request_headers_raw:
                raise ValueError('No HTTP headers found, you must specify at least Host for this to be a valid HTTP request')
        for raw_header in request_headers_raw:
            header, value = raw_header.split(':',1)
            request_headers.update({header: value.lstrip()})
