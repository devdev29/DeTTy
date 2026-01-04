import re
import inspect

from typing import Annotated, Optional, Callable, get_origin, get_args

from pydantic import BaseModel

from app.exceptions import PathAlreadyExistsError, MissingPathParameterError, PathNotFoundError
from app.http_response import HttpResponse
from app.models import FunctionParameters, PathParameter, QueryParameter, HeaderParameter, BodyParameter

class PathRegistry:
    registered_paths = {}
    path_var_regex = re.compile('{([a-zA-Z_][a-zA-Z0-9_]*)}')
    PATH_PARAM_NODE_NAME = 'var'

    
    def match(self, path_string: str, method: str) -> tuple[Callable, FunctionParameters, dict[str, str]]:
        node_list = path_string.split('/')
        curr_node = self.registered_paths[method]
        path_params = {}

        for node_string in node_list:
            if node_string in curr_node.keys():
                curr_node = curr_node[node_string]
            elif self.PATH_PARAM_NODE_NAME in curr_node.keys():
                curr_node = curr_node[self.PATH_PARAM_NODE_NAME]
                path_params[curr_node['param_name']]=node_string
            else:
                raise PathNotFoundError(path_string)
        
        func = curr_node['function']
        field_info = curr_node['field_info']
        if func is not None:
            return func, field_info, path_params
        else:
            raise PathNotFoundError(path_string)
        
    def add_route(self, path_string: str, method: str, func: Callable, override: Optional[bool] = False):
    # investigate this regex -  re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")
    # this is being used to match paths in the starlette router
    #TODO: refactor this method, is a bit of a hot mess
        if not method in self.registered_paths.keys():
            self.registered_paths[method] = {} # Default for / path

        function_params = inspect.signature(func).parameters
        path_params = []

        prev_node = self.registered_paths[method]
        node_list = path_string.split('/')
        for node_string in node_list:
            path_param_name = node_string
            node_string = self.PATH_PARAM_NODE_NAME if self.path_var_regex.match(node_string) else node_string
            if node_string is self.PATH_PARAM_NODE_NAME:
                print("added path_param "+path_param_name)
                path_params.append(path_param_name[1:-1])
            if not node_string in prev_node.keys():
                #Case when the path string is new
                if node_string is not self.PATH_PARAM_NODE_NAME:
                    curr_node = {'function': None}
                    prev_node[node_string] = curr_node
                else:
                    param_name = path_param_name[1:-1] # retaining the name of the path variable while excluding the curly braces { param }
                    if param_name not in function_params:
                        raise MissingPathParameterError(param_name)
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
        #Register metadata about the function parameters
        prev_node['field_info'] = self.extract_field_info(func, path_params)
        #If there are no problems then proceed to set the function to the one user gave
        prev_node['function'] = func

    def extract_field_info(self, func: Callable, path_params_list: list[str]) -> FunctionParameters:
        field_info = FunctionParameters()
        print("list passed "+str(path_params_list))
        for param_name, param in inspect.signature(func).parameters.items():
            base_type = param.annotation
            param_class = None
            if get_origin(param.annotation) is Annotated:
                args = get_args(param.annotation)
                base_type = args[0]
                if len(args) > 1:
                    param_class = args[1]
            if not param_class:
                if param_name in path_params_list:
                    param_class = PathParameter(field_name=param_name, annotation=base_type)
                    field_info.path_arguments[param_name] = param_class
                elif isinstance(base_type, (BaseModel, list, dict, tuple)):
                    param_class = BodyParameter(field_name=param_name, annotation=base_type, default_value=param.default)
                    field_info.body_arguments[param_name] = param_class
                else:
                    param_class = QueryParameter(field_name=param_name, annotation=base_type, default_value=param.default)
                    field_info.query_arguments[param_name] = param_class
            else:
                #User defined parameter class, defined inside Annotated
                param_class.field_name = param_name
                param_class.annotation = base_type
                param_class.default_value = param.default
                field_info.argument_category(param_class.category)[param_name] = param_class
            field_info.arguments.append(param_class)
        return field_info
