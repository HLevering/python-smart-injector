import inspect
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Type

from smart_injector.config.backend import Bindings
from smart_injector.config.backend import ConfigVisibility
from smart_injector.config.backend import FactoryArgs
from smart_injector.config.backend import Instances
from smart_injector.config.backend import Lifetimes
from smart_injector.config.backend import TypeWithContext
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
    def __init__(self, instances: Instances):
        self._instances = instances

    def can_handle_type(self, context: DependencyContext) -> bool:
        return (
            True if self._instances.has_instance(context.type_with_context()) else False
        )

    def handle(self, context: DependencyContext) -> T:
        return self._instances.get_instance(context.type_with_context())


class BindingHandler(Handler):
    def __init__(self, resolver: Resolver, bindings: Bindings):
        self._resolver = resolver
        self._bindings = bindings

    def can_handle_type(self, context: DependencyContext) -> bool:
        return (
            True
            if context.a_type
            is not self._bindings.get_binding(context.type_with_context())
            else False
        )

    def handle(self, context: DependencyContext) -> S:
        return self._resolver.get_new_instance(
            context.get_new_bind_context(
                self._bindings.get_binding(context.type_with_context())
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


class InstanceFactory:
    def __init__(self, resolver: Resolver, args: FactoryArgs):
        self._resolver = resolver
        self._args = args

    def create(self, context: DependencyContext) -> T:
        return context.a_type(
            **self._dependency_instances(context),
            **self._args.get_factory_args(context.type_with_context())
        )

    def _dependency_instances(self, context: DependencyContext) -> Dict[str, Any]:
        return {
            name: self._resolver.get_new_instance(
                context.get_new_dependency_context(dependent)
            )
            for name, dependent in dependencies(context.a_type).items()
            if name not in self._args.get_factory_args(context.type_with_context())
        }


class NewInstanceHandler(Handler):
    def __init__(self, factory: InstanceFactory):
        self._factory = factory

    def can_handle_type(self, context: DependencyContext) -> bool:
        return True

    def handle(self, context: DependencyContext) -> T:
        return self._factory.create(context)


class SingletonHandler(Handler):
    def __init__(
        self,
        lifetimes: Lifetimes,
        instances: Instances,
        instance_factory: InstanceFactory,
    ):
        self._lifetimes = lifetimes
        self._instances = instances
        self._instance_factory = instance_factory

    def can_handle_type(self, context: DependencyContext) -> bool:
        return True if self._is_singleton(context) else False

    def handle(self, context: DependencyContext) -> T:
        if self._singleton_not_created(context):
            self._create_singleton(context)
        return self._get_singleton(context)

    def _is_singleton(self, context: DependencyContext):
        return self._lifetimes.is_singleton(self._local_context(context))

    def _singleton_not_created(self, context: DependencyContext) -> bool:
        return not self._instances.has_instance(context.type_with_context())

    def _create_singleton(self, context: DependencyContext):
        self._instances.set_instance(
            self._instance_context(context), self._instance_factory.create(context)
        )

    def _instance_context(self, context: DependencyContext) -> TypeWithContext:
        if (
            self._lifetimes.visibility(context.type_with_context())
            is ConfigVisibility.LOCAL
        ):
            return self._local_context(context)
        else:
            return self._non_local_context(context)

    def _get_singleton(self, context: DependencyContext) -> T:
        return self._instances.get_instance(self._local_context(context))

    @abstractmethod
    def _local_context(self, context: DependencyContext) -> TypeWithContext:
        pass

    @abstractmethod
    def _non_local_context(self, context: DependencyContext) -> TypeWithContext:
        pass


class SingletonBaseTypeHandler(SingletonHandler):
    def _local_context(self, context: DependencyContext) -> TypeWithContext:
        return context.base_type_with_context()

    def _non_local_context(self, context: DependencyContext) -> TypeWithContext:
        return context.context_free_base_type()


class SingletonEffectiveHandler(SingletonHandler):
    def _local_context(self, context: DependencyContext) -> TypeWithContext:
        return context.type_with_context()

    def _non_local_context(self, context: DependencyContext) -> TypeWithContext:
        return context.context_free_type()
