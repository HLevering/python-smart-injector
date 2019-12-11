from typing import Callable
from typing import TypeVar

from smart_injector.config.user import Config
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

    def configure(self, config: Config):
        """ override this method in your own container class. The config parameter is an object which gives you plenty of
        methods to configure your container"""
        pass

    def get(self, a_type: Callable[..., T]) -> T:
        """get an instance of type a_type from the DI container. The instance of a_type is assembled according to your
        configuration rules which you specified in the configure method"""
        return self.__resolver.get_instance(a_type)
