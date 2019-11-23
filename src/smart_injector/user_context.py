import inspect
from typing import Any
from typing import Callable
from typing import TypeVar
from typing import cast

from smart_injector.register import Register
from smart_injector.scope import Scope
from smart_injector.utility import get_return_type

T = TypeVar("T")
S = TypeVar("S")


class Context:
    """ context object for the user, where the user can explicitly configure the container"""

    def __init__(self, register: Register):
        self._register = register

    def bind(
        self,
        a_type: Callable[..., T],
        to_type: Callable[..., S],
        scope: Scope = Scope.DEFAULT,
    ):
        if a_type not in inspect.getmro(cast(type, to_type)):
            raise TypeError(
                "{to_type} must be a subclass of {a_type}".format(
                    to_type=to_type, a_type=a_type
                )
            )
        self._register.set_binding(a_type, to_type)
        self._register.set_scope(a_type, scope)

    def set_scope(self, a_type: Callable[..., T], scope: Scope):
        self._register.set_scope(a_type, scope)

    def transient(self, a_type: Callable[..., T], **kwargs: Any):
        self._register.set_factory_args(a_type, kwargs)
        self._register.set_scope(a_type, scope=Scope.TRANSIENT)

    def singleton(self, a_type: Callable[..., T], **kwargs: Any):
        self._register.set_factory_args(a_type, kwargs)
        self._register.set_scope(a_type, scope=Scope.SINGLETON)

    def instance(self, a_type: Callable[..., T], instance: T):
        self._register.set_instance(a_type, instance)

    def callable(self, a_type: Callable[..., T], scope=Scope.DEFAULT, **kwargs: Any):
        return_type = get_return_type(a_type)
        if return_type is None:
            raise TypeError("only callables with return annotation are allowed")
        self._register.set_binding(return_type, a_type)
        self._register.set_scope(return_type, scope)
        self._register.set_factory_args(a_type, kwargs)

    def dependency(self, a_type: Callable[..., T]):
        self._register.add_dependency(a_type)
