"""
Test PathRegistry functionality.
"""

import sys
from pathlib import Path as FilePath

# Add parent directory to path
sys.path.insert(0, str(FilePath(__file__).parent.parent))

import pytest
from app.path_registry import PathRegistry
from app.exceptions import PathAlreadyExistsError, PathNotFoundError


@pytest.fixture
def fresh_registry():
    """Create a fresh PathRegistry instance with clean state."""
    pr = PathRegistry()
    pr.registered_paths = {}  # Reset class-level state
    return pr


def test_add_route_basic(fresh_registry):
    """Test basic route registration."""
    pr = fresh_registry
    
    def echo_animal(id: str):
        return id
    
    pr.add_route('/register/animal/{id}', 'GET', echo_animal)
    
    # Should be able to match the route
    func, field_info, path_params = pr.match('/register/animal/dog', 'GET')
    
    assert func == echo_animal
    assert path_params == {'id': 'dog'}
    assert 'id' in field_info.path_arguments


def test_add_multiple_routes(fresh_registry):
    """Test registering multiple routes."""
    pr = fresh_registry
    
    def echo_animal(id: str):
        return id
    
    def echo_person(id: str):
        return id
    
    def says_hi():
        return 'Hi!'
    
    pr.add_route('/register/animal/{id}', 'GET', echo_animal)
    pr.add_route('/register/person/{id}', 'GET', echo_person)
    pr.add_route('/person/devansh', 'GET', says_hi)
    
    # Test animal route
    func1, _, params1 = pr.match('/register/animal/dog', 'GET')
    assert func1 == echo_animal
    assert params1 == {'id': 'dog'}
    
    # Test person route with param
    func2, _, params2 = pr.match('/register/person/devansh', 'GET')
    assert func2 == echo_person
    assert params2 == {'id': 'devansh'}
    
    # Test person route without param
    func3, _, params3 = pr.match('/person/devansh', 'GET')
    assert func3 == says_hi
    assert params3 == {}


def test_path_not_found(fresh_registry):
    """Test that non-existent paths raise PathNotFoundError."""
    pr = fresh_registry
    
    def says_hi():
        return 'Hi!'
    
    pr.add_route('/person/devansh', 'GET', says_hi)
    
    with pytest.raises(PathNotFoundError):
        pr.match('/person/anyone', 'GET')


def test_already_registered_path(fresh_registry):
    """Test that duplicate path registration raises PathAlreadyExistsError."""
    pr = fresh_registry
    
    def func1(id: str):
        return id
    
    def func2(id: str):
        return id
    
    pr.add_route('/register/person/{id}', 'GET', func1)
    
    with pytest.raises(PathAlreadyExistsError):
        pr.add_route('/register/person/{id}', 'GET', func2)


def test_override_route(fresh_registry):
    """Test that override parameter allows replacing existing routes."""
    pr = fresh_registry
    
    def func1():
        return 'first'
    
    def func2():
        return 'second'
    
    pr.add_route('/test', 'GET', func1)
    pr.add_route('/test', 'GET', func2, override=True)
    
    func, _, _ = pr.match('/test', 'GET')
    assert func == func2


def test_different_http_methods(fresh_registry):
    """Test that same path with different methods works."""
    pr = fresh_registry
    
    def get_handler():
        return 'GET'
    
    def post_handler():
        return 'POST'
    
    pr.add_route('/api/resource', 'GET', get_handler)
    pr.add_route('/api/resource', 'POST', post_handler)
    
    func1, _, _ = pr.match('/api/resource', 'GET')
    func2, _, _ = pr.match('/api/resource', 'POST')
    
    assert func1 == get_handler
    assert func2 == post_handler


def test_multiple_path_params(fresh_registry):
    """Test routes with multiple path parameters."""
    pr = fresh_registry
    
    def multi_param(user_id: str, post_id: str):
        return f"{user_id}/{post_id}"
    
    pr.add_route('/users/{user_id}/posts/{post_id}', 'GET', multi_param)
    
    func, field_info, params = pr.match('/users/john/posts/42', 'GET')
    
    assert func == multi_param
    assert params == {'user_id': 'john', 'post_id': '42'}
    assert 'user_id' in field_info.path_arguments
    assert 'post_id' in field_info.path_arguments


def test_root_path(fresh_registry):
    """Test root path registration."""
    pr = fresh_registry
    
    def root():
        return 'root'
    
    pr.add_route('/', 'GET', root)
    
    func, _, params = pr.match('/', 'GET')
    
    assert func == root
    assert params == {}
