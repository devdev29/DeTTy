class HttpMethods:
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'

# TODO: Please find a way to make HttpStatusCodes and HttpReasonPhrases a single class, this is horrible :')))))
class HttpStatusCodes:
    OK = '200'
    CREATED = '201'
    BAD_REQUEST = '400'
    UNAUTHORIZED = '401'
    NOT_FOUND = '404'
    METHOD_NOT_ALLOWED = '405'
    INTERNAL_SERVER_ERROR = '500'

class HttpReasonPhrases:
    OK = 'OK'
    CREATED = 'Created'
    BAD_REQUEST = 'Bad Request'
    UNAUTHORIZED = 'Unauthorized'
    NOT_FOUND = 'Not Found'
    METHOD_NOT_ALLOWED = 'Method Not Allowed'
    INTERNAL_SERVER_ERROR = 'Internal Server Error'
