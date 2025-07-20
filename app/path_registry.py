import re
import inspect

from typing import Optional

from exceptions import PathAlreadyExistsError, ArgumentCountMismatchError, PathNotFoundError

class PathRegistry:
    registered_paths = {}
    path_var_regex = re.compile('{([a-zA-Z_][a-zA-Z0-9_]*)}')
    PATH_PARAM_NODE_NAME = 'var'

    def register(self, path_string: str, method: str, override: Optional[bool] = False):
        '''
        Decorator function for the internal add_route method to allow patterns like
        @pr.register('/register/person/{id}', 'GET')
        def echo(id: str):
            return id
        '''
        def decorator(func):
            self.add_route(
                path_string=path_string,
                method=method,
                func=func,
                override=override
            )
            return func
        return decorator
    
    def evaluate(self, path_string: str, method: str):
        node_list = path_string.split('/')
        curr_node = self.registered_paths[method]
        func_args = {}

        for node_string in node_list:
            if node_string in curr_node.keys():
                curr_node = curr_node[node_string]
            elif self.PATH_PARAM_NODE_NAME in curr_node.keys():
                curr_node = curr_node[self.PATH_PARAM_NODE_NAME]
                func_args[curr_node['param_name']]=node_string
            else:
                raise PathNotFoundError(path_string)
        
        func = curr_node['function']
        if func is not None:
            return func(**func_args)
        else:
            raise PathNotFoundError(path_string)
        
    def add_route(self, path_string: str, method: str, func, override: Optional[bool] = False):
    # investigate this regex -  re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")
    # this is being used to match paths in the starlette router
    #TODO: refactor this method, is a bit of a hot mess
        if not method in self.registered_paths.keys():
            self.registered_paths[method] = {} # Default for / path

        n_params = 0 # number of path parameters sent in the path
        function_params = len(inspect.signature(func).parameters) # number of parameters in the function passed

        prev_node = self.registered_paths[method]
        node_list = path_string.split('/')
        for node_string in node_list:
            path_param_name = node_string
            node_string = self.PATH_PARAM_NODE_NAME if self.path_var_regex.match(node_string) else node_string
            if not node_string in prev_node.keys():
                #Case when the path string is new
                if node_string is not self.PATH_PARAM_NODE_NAME:
                    curr_node = {'function': None}
                    prev_node[node_string] = curr_node
                else:
                    n_params += 1
                    param_name = path_param_name[1:-1] # retaining the name of the path variable while excluding the curly braces { param }
                    curr_node = {'function': None, 'param_name': param_name}
                    prev_node[self.PATH_PARAM_NODE_NAME] = curr_node
                prev_node = curr_node
            else: 
                #Case when this path string already exists
                #nothing needs to be done as it already exists in the correct form in the correct place
                prev_node = prev_node[node_string]
        #Check if path has been previously registered by checking if its method is None or not
        if prev_node['function'] is not None and not override:
            raise PathAlreadyExistsError(path_string)
        elif n_params != function_params:
            raise ArgumentCountMismatchError(n_params, function_params)
        #If there are no problems then proceed to set the function to the one user gave
        prev_node['function'] = func

if __name__=='__main__':
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
    
    # pr.register('/register/person/{id}', 'GET', echo)
    # pr.register('/register/animal/{id}', 'GET', echo)
    print(pr.registered_paths)
    dog = pr.evaluate('/register/animal/dog', 'GET')
    person = pr.evaluate('/register/person/shubh', 'GET')
    devansh = pr.evaluate('/person/devansh', 'GET')
    print(dog, person, devansh)
