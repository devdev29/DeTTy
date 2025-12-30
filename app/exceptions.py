from abc import ABC, abstractmethod

from app.http_constants import HttpStatus

class ExternalError(Exception, ABC):
    def __init__(self, code: str, reason_phrase: str):
        self.code = code
        self.reason_phrase = reason_phrase
    
    @abstractmethod
    def __str__(self) -> str:
        ...
    
#EXTERNAL ERRORS
#All external errors must have an HTTP status code associated with them
class NoHeadersFoundError(ExternalError):
    def __init__(self):
        super().__init__(HttpStatus.BAD_REQUEST.code, HttpStatus.BAD_REQUEST.phrase)
    def __str__(self):
        return 'No headers found on the request'

class InvalidBodyError(ExternalError):
    def __init__(self, request_string):
        super().__init__(HttpStatus.BAD_REQUEST.code, HttpStatus.BAD_REQUEST.phrase)
        self.request_string = request_string
    def __str__(self):
        return f'This body string is invalid w.r.t to the HTTP format: {self.request_string}'
   
class UnexpectedBodyError(Exception):
    def __init__(self, body_string):
        super().__init__(HttpStatus.UNPROCESSABLE_ENTITY.code, HttpStatus.UNPROCESSABLE_ENTITY.phrase)
        self.body_string = body_string
    def __str__(self):
        return f'This body string cannot be loaded into the expected entity: {self.body_string}'

class PathNotFoundError(ExternalError):
    def __init__(self, path_string):
        super().__init__(HttpStatus.NOT_FOUND.code, HttpStatus.NOT_FOUND.phrase)
        self.path_string = path_string
    def __str__(self):
        return f'The given path was not found: {self.path_string}'

#INTERNAL ERRORS        
class PathAlreadyExistsError(Exception):
    def __init__(self, path: str):
        self.path = path
    def __str__(self):
        return f'The path trying to be reigstered already exists: {self.path}'

class MissingPathParameterError(Exception):
    def __init__(self, path_params: set[str]):
        self.path_params = path_params
    def __str__(self):
        return f'The given function does not take these path parameters as arguments - {self.path_params}'
