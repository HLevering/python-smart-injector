from typing import Callable
from typing import TypeVar

from smart_injector.backend import Resolver
from smart_injector.user_context import Context

T = TypeVar("T")
S = TypeVar("S")


class StaticContainer:
    def __init__(self, resolver: Resolver):
        self.__resolver = resolver

    def configure(self, context: Context):
        pass

    def get(self, a_type: Callable[..., T]) -> T:
        return self.__resolver.get_instance(a_type)
