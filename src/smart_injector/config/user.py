import inspect
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import cast

from smart_injector.config.backend import ConfigBackend
from smart_injector.lifetime import Lifetime
from smart_injector.types import TypeWithContext
from smart_injector.utility import get_return_type

T = TypeVar("T")
S = TypeVar("S")

Where = Optional[Type[T]]


def is_base_class(base: Callable[..., T], subclass: Callable[..., S]) -> bool:
    if base in inspect.getmro(cast(type, subclass)):
        return True
    return False


class Config:
    """ context object for the user, which is used to explicitly configure injection behavior"""

    def __init__(self, backend: ConfigBackend):
        self._backend = backend

    def bind(
        self,
        a_type: Callable[..., T],
        to_type: Callable[..., S],
        lifetime: Lifetime = Lifetime._INTERNAL_DEFAULT,
        where: Where = None,
    ):
        """ Instead of a_type to_type will be used for injection. to_type must be a subclass type of a_type """
        if not is_base_class(a_type, to_type):
            raise TypeError(
                "{to_type} must be a subclass of {a_type}".format(
                    to_type=to_type, a_type=a_type
                )
            )
        self._backend.bindings.set_binding(TypeWithContext(a_type, where), to_type)
        self._backend.lifetimes.set_lifetime(
            TypeWithContext(a_type, where=where), lifetime
        )

    def set_lifetime(
        self, a_type: Callable[..., T], lifetime: Lifetime, where: Where = None
    ):
        """ set scope for a_type"""
        self._backend.lifetimes.set_lifetime(TypeWithContext(a_type, where), lifetime)

    def transient(self, a_type: Callable[..., T], where: Where = None, **kwargs: Any):
        """ provide a factory for a_type"""
        self._backend.factory_args.set_factory_args(
            TypeWithContext(a_type, where), kwargs
        )
        self._backend.lifetimes.set_lifetime(
            TypeWithContext(a_type, where), lifetime=Lifetime.TRANSIENT
        )

    def singleton(self, a_type: Callable[..., T], where: Where = None, **kwargs: Any):
        self._backend.factory_args.set_factory_args(
            TypeWithContext(a_type, where), kwargs
        )
        self._backend.lifetimes.set_lifetime(
            TypeWithContext(a_type, where), lifetime=Lifetime.SINGLETON
        )

    def instance(self, a_type: Callable[..., T], instance: T, where: Where = None):
        self._backend.instances.set_instance(TypeWithContext(a_type, where), instance)

    def callable(
        self,
        a_type: Callable[..., T],
        lifetime=Lifetime._INTERNAL_DEFAULT,
        where: Where = None,
        **kwargs: Any
    ):
        return_type = get_return_type(a_type)
        if return_type is None:
            raise TypeError("only callables with return annotation are allowed")
        self._backend.bindings.set_binding(TypeWithContext(return_type, where), a_type)
        self._backend.lifetimes.set_lifetime(TypeWithContext(a_type, where), lifetime)
        self._backend.factory_args.set_factory_args(
            TypeWithContext(a_type, where), kwargs
        )

    def dependency(self, a_type: Callable[..., T]):
        self._backend.dependencies.add_dependency(a_type)

    def set_arguments(
        self, a_type: Callable[..., T], where: Where = None, **kwargs: Any
    ):
        self._backend.factory_args.set_factory_args(
            TypeWithContext(a_type, where), kwargs
        )
