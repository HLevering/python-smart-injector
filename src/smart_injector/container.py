import inspect
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

T = TypeVar("T")


class StaticContainer:
    def __init__(self, my_builtins: List[Type]):
        self._builtins = my_builtins

    def _get_signature(self, a_type: Callable[..., T]) -> Dict[str, Type[Any]]:
        return {
            parameter.name: parameter.annotation
            for parameter in inspect.signature(a_type).parameters.values()
        }

    def _build_dependencies(self, a_type: Callable[..., T]) -> Dict[str, Type[Any]]:
        return {
            name: self.get(b_type)
            for name, b_type in self._get_signature(a_type).items()
        }

    def _default_construct(self, a_type: Callable[..., T]) -> T:
        return a_type()

    def get(self, a_type: Callable[..., T]) -> T:
        if a_type in self._builtins:
            return self._default_construct(a_type)
        dependency_instances = self._build_dependencies(a_type)
        return a_type(**dependency_instances)
