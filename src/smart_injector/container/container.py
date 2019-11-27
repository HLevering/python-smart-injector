from typing import Callable
from typing import TypeVar

from smart_injector.config.user import Config
from smart_injector.resolver.resolver import Resolver

T = TypeVar("T")
S = TypeVar("S")


class StaticContainer:
    def __init__(self, resolver: Resolver):
        self.__resolver = resolver

    def configure(self, config: Config):
        pass

    def get(self, a_type: Callable[..., T]) -> T:
        return self.__resolver.get_instance(a_type)
