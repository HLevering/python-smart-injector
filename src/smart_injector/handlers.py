import inspect
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Type

from smart_injector.backend import Resolver
from smart_injector.container import S
from smart_injector.container import T
from smart_injector.register import Register
from smart_injector.types import Handler
from smart_injector.types import LocalContext


def dependencies(a_type: Callable[..., T]) -> Dict[str, Type[Any]]:
    return {
        parameter.name: parameter.annotation
        for parameter in inspect.signature(a_type).parameters.values()
    }


class InstanceHandler(Handler):
    def __init__(self, register: Register):
        self._register = register

    def can_handle_type(self, context: LocalContext) -> bool:
        return True if self._register.has_instance(context.a_type) else False

    def handle(self, context: LocalContext) -> T:
        return self._register.get_instance(context.a_type)


class BindingHandler(Handler):
    def __init__(self, resolver: Resolver, register: Register):
        self._resolver = resolver
        self._register = register

    def can_handle_type(self, context: LocalContext) -> bool:
        return (
            True
            if context.a_type is not self._register.get_binding(context.a_type)
            else False
        )

    def handle(self, context: LocalContext) -> S:
        return self._resolver.get_new_instance(
            context.get_new(self._register.get_binding(context.a_type))
        )


class AbstractTypeHandler(Handler):
    def can_handle_type(self, context: LocalContext) -> bool:
        return True if inspect.isabstract(context.a_type) else False

    def handle(self, context: LocalContext) -> T:
        raise TypeError("No binding for abstract base {0}".format(context.a_type))


class BuiltinsTypeHandler(Handler):
    def __init__(self, my_builtins: List[Type[Any]]):
        self._my_builtins = my_builtins

    def can_handle_type(self, context: LocalContext) -> bool:
        return True if context.a_type in self._my_builtins else False

    def handle(self, context: LocalContext) -> T:
        return context.a_type()


class DefaultTypeHandler(Handler):
    def __init__(self, resolver: Resolver, register: Register):
        self._resolver = resolver
        self._register = register

    def can_handle_type(self, context: LocalContext) -> bool:
        return True

    def handle(self, context: LocalContext) -> T:
        return context.a_type(
            **self._dependency_instances(context),
            **self._register.get_factory_args(context.a_type)
        )

    def _dependency_instances(self, context: LocalContext) -> Dict[str, Any]:
        return {
            name: self._resolver.get_new_instance(context.get_new(dependent))
            for name, dependent in dependencies(context.a_type).items()
            if name not in self._register.get_factory_args(context.a_type)
        }


class SingletonBaseHandler(DefaultTypeHandler):
    def can_handle_type(self, context: LocalContext) -> bool:
        return True if self._register.is_singleton(context.base_type) else False

    def handle(self, context: LocalContext) -> T:
        if not self._register.has_instance(context.base_type):
            self._register.set_instance(context.base_type, super().handle(context))
        return self._register.get_instance(context.base_type)


class SingletonEffectiveHandler(DefaultTypeHandler):
    def can_handle_type(self, context: LocalContext) -> bool:
        return True if self._register.is_singleton(context.a_type) else False

    def handle(self, context: LocalContext) -> T:
        if not self._register.has_instance(context.a_type):
            self._register.set_instance(context.a_type, super().handle(context))
        return self._register.get_instance(context.a_type)
