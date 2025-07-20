from http_constants import HttpStatusCodes, HttpReasonPhrases

#EXTERNAL ERRORS
#All external errors must have an HTTP status code associated with them
class NoHeadersFoundError(ValueError):
    def __init__(self):
        self.code = HttpStatusCodes.BAD_REQUEST
        self.reason_phrase = HttpReasonPhrases.BAD_REQUEST
    def __str__(self):
        return 'No headers found on the request'

class InvalidBodyError(Exception):
    def __init__(self, request_string):
        self.request_string = request_string
        self.code = HttpStatusCodes.BAD_REQUEST
        self.reason_phrase = HttpReasonPhrases.BAD_REQUEST
    def __str__(self):
        return f'This body string is invalid w.r.t to the HTTP format: {self.request_string}'
   
class PathNotFoundError(Exception):
    def __init__(self, path_string):
        self.path_string = path_string
        self.code = HttpStatusCodes.NOT_FOUND
        self.reason_phrase = HttpReasonPhrases.NOT_FOUND
    def __str__(self):
        return f'The given path was not found: {self.path_string}'

#INTERNAL ERRORS        
class PathAlreadyExistsError(Exception):
    def __init__(self, path: str):
        self.path = path
    def __str__(self):
        return f'The path trying to be reigstered already exists: {self.path}'

class ArgumentCountMismatchError(Exception):
    def __init__(self, path_args: int, func_args: int):
        self.path_args = path_args
        self.func_args = func_args
    def __str__(self):
        return f'The number of arguments provided in the path string {self.path_args} is different from the number provided in the function {self.func_args}'
