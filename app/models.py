from ast import Param
import inspect
from typing import Any, Type, Optional
from enum import Enum
from dataclasses import dataclass, field

from pydantic import TypeAdapter, ValidationError, type_adapter

allowed_text_types = [str, int, float, bool]

# Use inspect.Parameter.empty as the sentinel
EMPTY_DEFAULT = inspect.Parameter.empty

class ParamCategory(Enum):
    PATH = 'PATH'
    QUERY = 'QUERY'
    HEADER = 'HEADER'
    BODY = 'BODY'

@dataclass
class AnnotatedParameter:
    field_name: str = ""
    annotation: Optional[Type[Any]] = None
    category: Optional[ParamCategory] = None
    default_value: Any = field(default_factory=lambda: EMPTY_DEFAULT)

    def __post_init__(self):
        if self.default_value is not EMPTY_DEFAULT:
            print(self.default_value)
            self.default_value = self._type_adapter.validate_python(self.default_value)

    @property
    def _type_adapter(self) -> TypeAdapter[Any]:
        if self.annotation is not None:
            return TypeAdapter(self.annotation)
        raise ValueError("cannot create type adapter without annotation")

    def validate_value(self, value: Any) -> Any:
        try:
            return self._type_adapter.validate_python(value)
        except ValidationError as ve:
            raise ValidationError(f"Invalid value for argument {self.field_name}: {ve}")
@dataclass
class PathParameter(AnnotatedParameter):
    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.PATH
        assert self.default_value is None or self.default_value is EMPTY_DEFAULT, "Path arguments cannot have a default value"
        assert self.annotation in allowed_text_types, "Path arguments must be a text type"
@dataclass
class QueryParameter(AnnotatedParameter):
    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.QUERY
        assert self.annotation in allowed_text_types, "Query arguments must be a text type"
@dataclass
class HeaderParameter(AnnotatedParameter):
    header_name: str = field(default="", kw_only=True)  

    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.HEADER
@dataclass
class BodyParameter(AnnotatedParameter):
    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.BODY

@dataclass
class FunctionParameters:
    arguments: list[AnnotatedParameter] = field(default_factory = list[AnnotatedParameter])
    path_arguments: dict[str, PathParameter] = field(default_factory=dict[str, PathParameter])
    query_arguments: dict[str, QueryParameter] = field(default_factory=dict[str, QueryParameter])
    header_arguments: dict[str, HeaderParameter] = field(default_factory=dict[str, HeaderParameter])
    body_arguments: dict[str, BodyParameter] = field(default_factory=dict[str, BodyParameter])
    _argument_category: dict[str, AnnotatedParameter] = field(default_factory=dict[str, AnnotatedParameter])

    def __post_init__(self):
        self._argument_category.update({ParamCategory.BODY: self.body_arguments, 
        ParamCategory.HEADER: self.header_arguments, 
        ParamCategory.PATH: self.path_arguments, 
        ParamCategory.QUERY: self.query_arguments})

    def argument_category(self, category: ParamCategory) -> list[AnnotatedParameter]:
        return self._argument_category.get(category)

    def get_argument_by_name(self, name: str) -> AnnotatedParameter:
        for argument in self.arguments:
            if argument.field_name == name:
                return argument
        raise ValueError(f"Argument with name {name} not found")
    
    def _get_arguments_by_annotation(self, annotation: Type[Any]) -> list[AnnotatedParameter]:
        return [argument for argument in self.arguments if argument.annotation == annotation]
