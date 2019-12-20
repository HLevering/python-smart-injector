from typing import Callable
from typing import TypeVar

from smart_injector.resolver.resolver import Resolver

T = TypeVar("T")
S = TypeVar("S")


class StaticContainer:
    """DI Container. Used by the user to get instances of types.

    To get your own container. Create a new class inherited from this class and override configure method
    """

    def __init__(self, resolver: Resolver):
        """You should not create an instance of your DI container own your own. Use the factory function create_container
        instead"""
        self.__resolver = resolver

    def get(self, a_type: Callable[..., T]) -> T:
        """
        Get an instance of type `T`

        :param a_type: either a class `T` or a function returning a `T`
        :return: an instance of `T`
        """
        return self.__resolver.get_instance(a_type)
