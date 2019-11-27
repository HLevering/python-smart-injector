import inspect
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Type

from smart_injector.config.backend import ConfigBackend
from smart_injector.config.backend import ConfigVisibility
from smart_injector.container.container import S
from smart_injector.container.container import T
from smart_injector.resolver.resolver import Resolver
from smart_injector.types import DependencyContext
from smart_injector.types import Handler


def dependencies(a_type: Callable[..., T]) -> Dict[str, Type[Any]]:
    return {
        parameter.name: parameter.annotation
        for parameter in inspect.signature(a_type).parameters.values()
    }


class InstanceHandler(Handler):
    def __init__(self, register: ConfigBackend):
        self._register = register

    def can_handle_type(self, context: DependencyContext) -> bool:
        return (
            True if self._register.has_instance(context.type_with_context()) else False
        )

    def handle(self, context: DependencyContext) -> T:
        return self._register.get_instance(context.type_with_context())


class BindingHandler(Handler):
    def __init__(self, resolver: Resolver, register: ConfigBackend):
        self._resolver = resolver
        self._register = register

    def can_handle_type(self, context: DependencyContext) -> bool:
        return (
            True
            if context.a_type
            is not self._register.get_binding(context.type_with_context())
            else False
        )

    def handle(self, context: DependencyContext) -> S:
        return self._resolver.get_new_instance(
            context.get_new_bind_context(
                self._register.get_binding(context.type_with_context())
            )
        )


class AbstractTypeHandler(Handler):
    def can_handle_type(self, context: DependencyContext) -> bool:
        return True if inspect.isabstract(context.a_type) else False

    def handle(self, context: DependencyContext) -> T:
        raise TypeError("No binding for abstract base {0}".format(context.a_type))


class BuiltinsTypeHandler(Handler):
    def __init__(self, my_builtins: List[Type[Any]]):
        self._my_builtins = my_builtins

    def can_handle_type(self, context: DependencyContext) -> bool:
        return True if context.a_type in self._my_builtins else False

    def handle(self, context: DependencyContext) -> T:
        return context.a_type()


class DefaultTypeHandler(Handler):
    def __init__(self, resolver: Resolver, register: ConfigBackend):
        self._resolver = resolver
        self._register = register

    def can_handle_type(self, context: DependencyContext) -> bool:
        return True

    def handle(self, context: DependencyContext) -> T:
        return context.a_type(
            **self._dependency_instances(context),
            **self._register.get_factory_args(context.type_with_context())
        )

    def _dependency_instances(self, context: DependencyContext) -> Dict[str, Any]:
        return {
            name: self._resolver.get_new_instance(
                context.get_new_dependency_context(dependent)
            )
            for name, dependent in dependencies(context.a_type).items()
            if name not in self._register.get_factory_args(context.type_with_context())
        }


class SingletonBaseTypeHandler(DefaultTypeHandler):
    def can_handle_type(self, context: DependencyContext) -> bool:
        return (
            True
            if self._register.is_singleton(context.base_type_with_context())
            else False
        )

    def handle(self, context: DependencyContext) -> T:

        if not self._register.has_instance(context.type_with_context()):
            if (
                self._register.get_scope_visibility(context.type_with_context())
                is ConfigVisibility.LOCAL
            ):
                context_based = context.base_type_with_context()
            else:
                context_based = context.context_free_base_type()
            self._register.set_instance(context_based, super().handle(context))
        return self._register.get_instance(context.base_type_with_context())


class SingletonEffectiveHandler(DefaultTypeHandler):
    def can_handle_type(self, context: DependencyContext) -> bool:
        return (
            True if self._register.is_singleton(context.type_with_context()) else False
        )

    def handle(self, context: DependencyContext) -> T:
        if not self._register.has_instance(context.type_with_context()):
            if (
                self._register.get_scope_visibility(context.type_with_context())
                is ConfigVisibility.LOCAL
            ):
                type_with_context = context.type_with_context()
            else:
                type_with_context = context.context_free_type()
            self._register.set_instance(type_with_context, super().handle(context))
        return self._register.get_instance(context.type_with_context())
