import inspect
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Type

from smart_injector.config.backend import Bindings
from smart_injector.config.backend import ConfigEntry
from smart_injector.config.backend import ConfigVisibility
from smart_injector.config.backend import FactoryArgs
from smart_injector.config.backend import Instances
from smart_injector.config.backend import Lifetimes
from smart_injector.container.container import S
from smart_injector.container.container import T
from smart_injector.resolver.resolver import Resolver
from smart_injector.types import Handler
from smart_injector.types import ResolveRequest


def dependencies(a_type: Callable[..., T]) -> Dict[str, Type[Any]]:
    """returns dependencies of a callable"""
    return {
        parameter.name: parameter.annotation
        for parameter in inspect.signature(a_type).parameters.values()
    }


class InstanceHandler(Handler):
    """return an a priori set instance for a type"""
    def __init__(self, instances: Instances):
        self._instances = instances

    def can_handle_type(self, request: ResolveRequest) -> bool:
        return (
            True
            if self._instances.has_instance(request.local_config_entry())
            else False
        )

    def handle(self, request: ResolveRequest) -> T:
        return self._instances.get_instance(request.local_config_entry())


class BindingHandler(Handler):
    def __init__(self, resolver: Resolver, bindings: Bindings):
        self._resolver = resolver
        self._bindings = bindings

    def can_handle_type(self, request: ResolveRequest) -> bool:
        return (
            True
            if request.real_type
            is not self._bindings.get_binding(request.local_config_entry())
            else False
        )

    def handle(self, request: ResolveRequest) -> S:
        return self._resolver.get_new_instance(
            request.new_request_with_same_origin(
                self._bindings.get_binding(request.local_config_entry())
            )
        )


class AbstractTypeHandler(Handler):
    def can_handle_type(self, request: ResolveRequest) -> bool:
        return True if inspect.isabstract(request.real_type) else False

    def handle(self, request: ResolveRequest) -> T:
        raise TypeError("No binding for abstract base {0}".format(request.real_type))


class BuiltinsTypeHandler(Handler):
    """handler for python builtin types"""
    def __init__(self, my_builtins: List[Type[Any]]):
        self._my_builtins = my_builtins

    def can_handle_type(self, request: ResolveRequest) -> bool:
        return True if request.real_type in self._my_builtins else False

    def handle(self, request: ResolveRequest) -> T:
        return request.real_type()


class InstanceFactory:
    def __init__(self, resolver: Resolver, args: FactoryArgs):
        self._resolver = resolver
        self._args = args

    def create(self, context: ResolveRequest) -> T:
        return context.real_type(
            **self._dependency_instances(context), **self._factory_args(context)
        )

    def _factory_args(self, context: ResolveRequest) -> Dict[str, Any]:
        return {
            name: value.get(self._resolver)
            for name, value in self._args.get_factory_args(
                context.local_config_entry()
            ).items()
        }

    def _dependency_instances(self, context: ResolveRequest) -> Dict[str, Any]:
        return {
            name: self._resolver.get_new_instance(
                context.get_new_dependency_context(dependent)
            )
            for name, dependent in dependencies(context.real_type).items()
            if name not in self._args.get_factory_args(context.local_config_entry())
        }


class NewInstanceHandler(Handler):
    def __init__(self, factory: InstanceFactory):
        self._factory = factory

    def can_handle_type(self, request: ResolveRequest) -> bool:
        return True

    def handle(self, request: ResolveRequest) -> T:
        return self._factory.create(request)


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

    def can_handle_type(self, request: ResolveRequest) -> bool:
        return True if self._is_singleton(request) else False

    def handle(self, request: ResolveRequest) -> T:
        if self._singleton_not_created(request):
            self._create_singleton(request)
        return self._get_singleton(request)

    def _is_singleton(self, context: ResolveRequest):
        return self._lifetimes.is_singleton(self._local_config_entry(context))

    def _singleton_not_created(self, context: ResolveRequest) -> bool:
        return not self._instances.has_instance(context.local_config_entry())

    def _create_singleton(self, context: ResolveRequest):
        self._instances.set_instance(
            self._instance_context(context), self._instance_factory.create(context)
        )

    def _instance_context(self, context: ResolveRequest) -> ConfigEntry:
        if (
            self._lifetimes.visibility(context.local_config_entry())
            is ConfigVisibility.LOCAL
        ):
            return self._local_config_entry(context)
        else:
            return self._global_config_entry(context)

    def _get_singleton(self, context: ResolveRequest) -> T:
        return self._instances.get_instance(self._local_config_entry(context))

    @abstractmethod
    def _local_config_entry(self, context: ResolveRequest) -> ConfigEntry:
        pass

    @abstractmethod
    def _global_config_entry(self, context: ResolveRequest) -> ConfigEntry:
        pass


class SingletonBaseTypeHandler(SingletonHandler):
    def _local_config_entry(self, context: ResolveRequest) -> ConfigEntry:
        return context.local_base_config_entry()

    def _global_config_entry(self, context: ResolveRequest) -> ConfigEntry:
        return context.global_base_config_entry()


class SingletonEffectiveHandler(SingletonHandler):
    def _local_config_entry(self, context: ResolveRequest) -> ConfigEntry:
        return context.local_config_entry()

    def _global_config_entry(self, context: ResolveRequest) -> ConfigEntry:
        return context.global_config_entry()
