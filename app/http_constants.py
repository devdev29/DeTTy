from typing import NamedTuple


class HttpMethods:
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'


class HttpStatusValue(NamedTuple):
    """Represents an HTTP status with code and reason phrase."""
    code: str
    phrase: str


class HttpStatus:
    """
    HTTP status codes with their reason phrases.
    
    Usage:
        HttpStatus.OK.code          # '200'
        HttpStatus.OK.phrase        # 'OK'
        HttpStatus.NOT_FOUND.code   # '404'
        HttpStatus.NOT_FOUND.phrase # 'Not Found'
    """
    # 2xx Success
    OK = HttpStatusValue('200', 'OK')
    CREATED = HttpStatusValue('201', 'Created')
    NO_CONTENT = HttpStatusValue('204', 'No Content')
    
    # 4xx Client Error
    BAD_REQUEST = HttpStatusValue('400', 'Bad Request')
    UNAUTHORIZED = HttpStatusValue('401', 'Unauthorized')
    NOT_FOUND = HttpStatusValue('404', 'Not Found')
    METHOD_NOT_ALLOWED = HttpStatusValue('405', 'Method Not Allowed')
    UNPROCESSABLE_ENTITY = HttpStatusValue('422', 'Unprocessable Entity')
    
    # 5xx Server Error
    INTERNAL_SERVER_ERROR = HttpStatusValue('500', 'Internal Server Error')


# Default HTTP status for each method
DEFAULT_METHOD_STATUS: dict[str, HttpStatusValue] = {
    HttpMethods.GET: HttpStatus.OK,
    HttpMethods.HEAD: HttpStatus.OK,
    HttpMethods.POST: HttpStatus.CREATED,
    HttpMethods.PUT: HttpStatus.OK,
    HttpMethods.DELETE: HttpStatus.NO_CONTENT,
    HttpMethods.OPTIONS: HttpStatus.OK,
}
