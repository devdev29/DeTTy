import pytest

from app.path_registry import PathRegistry
from app.exceptions import PathAlreadyExistsError, PathNotFoundError

pr = PathRegistry()

@pr.register('/register/animal/{id}', 'GET')
def echo_animal(id: str):
    return id

@pr.register('/register/person/{id}', 'GET')
def echo_person(id: str):
    return id

@pr.register('/person/devansh', 'GET')
def says_hi():
    return 'Hi!'

@pytest.fixture
def path_registry_fixture():
    return {'GET': {'': {'function': None, 'register': {'function': None, 'animal': {'function': None, 'var': {'function': echo_animal, 'param_name': 'id'}}, 'person': {'function': None, 'var': {'function': echo_person, 'param_name': 'id'}}}, 'person': {'function': None, 'devansh': {'function': says_hi}}}}}

def test_registry_creation(path_registry_fixture):
    assert pr.registered_paths == path_registry_fixture

def test_paths_with_params():
    assert pr.evaluate('/register/animal/dog', 'GET') == 'dog'
    assert pr.evaluate('/register/person/devansh') == 'devansh'

def test_path_normal():
    assert pr.evaluate('/person/devansh') == 'Hi!'

def test_non_existent_path():
    with pytest.raises(PathNotFoundError):
        pr.evaluate('/person/anyone')

def test_already_registered_path():
    with pytest.raises(PathAlreadyExistsError):
        pr.register('/register/person/{person_id}')
