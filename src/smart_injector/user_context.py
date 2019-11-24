import inspect
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import cast

from smart_injector.register import Register
from smart_injector.scope import Scope
from smart_injector.types import ContextBased
from smart_injector.utility import get_return_type

T = TypeVar("T")
S = TypeVar("S")

Where = Optional[Type[T]]


class Context:
    """ context object for the user, which is used to explicitly configure injection behavior"""

    def __init__(self, register: Register):
        self._default_register = register

    def bind(
        self,
        a_type: Callable[..., T],
        to_type: Callable[..., S],
        scope: Scope = Scope._INTERNAL_DEFAULT,
        where: Where = None,
    ):
        """ Instead of a_type to_type will be used for injection. to_type must be a subclass type of a_type """
        if a_type not in inspect.getmro(cast(type, to_type)):
            raise TypeError(
                "{to_type} must be a subclass of {a_type}".format(
                    to_type=to_type, a_type=a_type
                )
            )
        self._default_register.set_binding(ContextBased(a_type, where), to_type)
        self._default_register.set_scope(ContextBased(a_type, where=where), scope)

    def set_scope(self, a_type: Callable[..., T], scope: Scope, where: Where = None):
        """ set scope for a_type"""
        self._default_register.set_scope(ContextBased(a_type, where), scope)

    def transient(self, a_type: Callable[..., T], where: Where = None, **kwargs: Any):
        """ provide a factory for a_type"""
        self._default_register.set_factory_args(ContextBased(a_type, where), kwargs)
        self._default_register.set_scope(
            ContextBased(a_type, where), scope=Scope.TRANSIENT
        )

    def singleton(self, a_type: Callable[..., T], where: Where = None, **kwargs: Any):
        self._default_register.set_factory_args(ContextBased(a_type, where), kwargs)
        self._default_register.set_scope(
            ContextBased(a_type, where), scope=Scope.SINGLETON
        )

    def instance(self, a_type: Callable[..., T], instance: T, where: Where = None):
        self._default_register.set_instance(ContextBased(a_type, where), instance)

    def callable(
        self,
        a_type: Callable[..., T],
        scope=Scope._INTERNAL_DEFAULT,
        where: Where = None,
        **kwargs: Any
    ):
        return_type = get_return_type(a_type)
        if return_type is None:
            raise TypeError("only callables with return annotation are allowed")
        self._default_register.set_binding(ContextBased(return_type, where), a_type)
        self._default_register.set_scope(ContextBased(a_type, where), scope)
        self._default_register.set_factory_args(ContextBased(a_type, where), kwargs)

    def dependency(self, a_type: Callable[..., T]):
        self._default_register.add_dependency(a_type)
