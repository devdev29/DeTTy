"""
Test WSGI compliance for DeTTy framework.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from io import BytesIO
from app.detty import DeTTy
from app.models import Header
from typing import Annotated


def test_wsgi_interface():
    """Test that DeTTy implements WSGI interface correctly."""
    app = DeTTy()
    
    @app.register('/test', 'GET')
    def test_route():
        return "OK"
    
    @app.register('/echo/{message}', 'GET')
    def echo(message: str):
        return message
    
    @app.register('/user-agent', 'GET')
    def user_agent(ua: Annotated[str, Header(header_name='User-Agent')]):
        return ua
    
    # Test 1: Basic GET request
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/test',
        'QUERY_STRING': '',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.input': BytesIO(b''),
        'CONTENT_LENGTH': '0',
        'HTTP_HOST': 'localhost:4221',
    }
    
    responses = []
    def start_response(status, headers):
        responses.append((status, headers))
    
    result = app(environ, start_response)
    
    assert len(responses) == 1
    assert responses[0][0] == "200 OK"
    assert result == [b'OK']
    print("[PASS] Test 1: Basic GET request passed")
    
    # Test 2: Path parameters
    environ2 = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/echo/hello',
        'QUERY_STRING': '',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.input': BytesIO(b''),
        'CONTENT_LENGTH': '0',
        'HTTP_HOST': 'localhost:4221',
    }
    
    responses2 = []
    def start_response2(status, headers):
        responses2.append((status, headers))
    
    result2 = app(environ2, start_response2)
    
    assert len(responses2) == 1
    assert responses2[0][0] == "200 OK"
    assert result2 == [b'hello']
    print("[PASS] Test 2: Path parameters passed")
    
    # Test 3: Headers
    environ3 = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/user-agent',
        'QUERY_STRING': '',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.input': BytesIO(b''),
        'CONTENT_LENGTH': '0',
        'HTTP_HOST': 'localhost:4221',
        'HTTP_USER_AGENT': 'TestClient/1.0',
    }
    
    responses3 = []
    def start_response3(status, headers):
        responses3.append((status, headers))
    
    result3 = app(environ3, start_response3)
    
    assert len(responses3) == 1
    assert responses3[0][0] == "200 OK"
    assert result3 == [b'TestClient/1.0']
    print("[PASS] Test 3: Header extraction passed")
    
    # Test 4: 404 Not Found
    environ4 = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/nonexistent',
        'QUERY_STRING': '',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.input': BytesIO(b''),
        'CONTENT_LENGTH': '0',
        'HTTP_HOST': 'localhost:4221',
    }
    
    responses4 = []
    def start_response4(status, headers):
        responses4.append((status, headers))
    
    result4 = app(environ4, start_response4)
    
    assert len(responses4) == 1
    assert responses4[0][0] == "404 Not Found"
    print("[PASS] Test 4: 404 handling passed")
    
    print("\n[SUCCESS] All WSGI compliance tests passed!")


if __name__ == "__main__":
    test_wsgi_interface()

