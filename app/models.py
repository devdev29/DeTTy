import inspect

from typing import Any, Type, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from typing_extensions import override

from pydantic import TypeAdapter, ValidationError 
from pydantic_core import from_json


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
        self._type_adapter = TypeAdapter(self.annotation)
        if self.default_value is not EMPTY_DEFAULT:
            print(self.default_value)
            self.default_value = self._type_adapter.validate_python(self.default_value)

    @property
    def request_key(self) -> str:
        """The key used to look up this parameter's value in request data."""
        return self.field_name

    @property
    def has_default(self) -> bool:
        return self.default_value is not EMPTY_DEFAULT

    def validate_value(self, value: Any) -> Any:
        try:
            return self._type_adapter.validate_python(value)
        except ValidationError as ve:
            raise ValidationError(f"Invalid value for argument {self.field_name}: {ve}")
@dataclass
class Path(AnnotatedParameter):
    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.PATH
        assert self.default_value is None or self.default_value is EMPTY_DEFAULT, "Path arguments cannot have a default value"
        assert self.annotation in allowed_text_types, "Path arguments must be a text type"
@dataclass
class Query(AnnotatedParameter):
    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.QUERY
        assert self.annotation in allowed_text_types, "Query arguments must be a text type"
@dataclass
class Header(AnnotatedParameter):
    header_name: str = field(default="", kw_only=True)  

    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.HEADER

    @property
    def request_key(self) -> str:
        """Headers use header_name as the lookup key."""
        return self.header_name

@dataclass
class Body(AnnotatedParameter):
    def __post_init__(self):
        super().__post_init__()
        self.category = ParamCategory.BODY
    
    @override
    def validate_value(self, value: Union[str, bytes]) -> Any:
        data_dict = from_json(value, allow_partial=True)
        return super().validate_value(data_dict)


@dataclass
class FunctionParameters:
    arguments: list[AnnotatedParameter] = field(default_factory = list[AnnotatedParameter])
    path_arguments: dict[str, Path] = field(default_factory=dict[str, Path])
    query_arguments: dict[str, Query] = field(default_factory=dict[str, Query])
    header_arguments: dict[str, Header] = field(default_factory=dict[str, Header])
    body_arguments: dict[str, Body] = field(default_factory=dict[str, Body])
    response_argument: str = ''
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

