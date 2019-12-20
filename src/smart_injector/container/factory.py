from typing import Callable
from typing import List
from typing import Optional

from smart_injector.config.backend import Bindings
from smart_injector.config.backend import ConfigBackend
from smart_injector.config.backend import ConfigEntry
from smart_injector.config.backend import Dependencies
from smart_injector.config.backend import FactoryArgs
from smart_injector.config.backend import Instances
from smart_injector.config.backend import Lifetimes
from smart_injector.config.user import Config
from smart_injector.container.container import StaticContainer
from smart_injector.lifetime import Lifetime
from smart_injector.resolver.handlers import AbstractTypeHandler
from smart_injector.resolver.handlers import BindingHandler
from smart_injector.resolver.handlers import BuiltinsTypeHandler
from smart_injector.resolver.handlers import InstanceFactory
from smart_injector.resolver.handlers import InstanceHandler
from smart_injector.resolver.handlers import NewInstanceHandler
from smart_injector.resolver.handlers import SingletonBaseTypeHandler
from smart_injector.resolver.handlers import SingletonEffectiveHandler
from smart_injector.resolver.resolver import Resolver


def create_container(
    configure: Optional[Callable[[Config], None]] = None,
    default_lifetime=Lifetime.TRANSIENT,
    dependencies: Optional[List[object]] = None,
) -> StaticContainer:
    """
    Use this function to create a DI container.

    :param configure:
    :param default_lifetime:
    :param dependencies:
    :return:
    """
    if configure is None:
        configure = _default_config
    if dependencies is None:
        dependencies = []
    backend = _create_backend(default_lifetime)
    resolver = _create_resolver(backend)
    container = StaticContainer(resolver=resolver)
    configure(Config(backend=backend))
    _resolve_dependencies(backend, dependencies)
    return container


def _default_config(config: Config):
    pass


def _create_backend(default_lifetime: Lifetime) -> ConfigBackend:
    lifetimes = Lifetimes(default_lifetime)
    instances = Instances()
    bindings = Bindings()
    factory_args = FactoryArgs()
    _dependencies = Dependencies()
    return ConfigBackend(bindings, lifetimes, instances, factory_args, _dependencies)


def _create_resolver(backend: ConfigBackend):
    resolver = Resolver()
    instance_factory = InstanceFactory(resolver, backend.factory_args)
    resolver.add_type_handler(InstanceHandler(backend.instances))
    resolver.add_type_handler(BindingHandler(resolver, backend.bindings))
    resolver.add_type_handler(
        SingletonBaseTypeHandler(backend.lifetimes, backend.instances, instance_factory)
    )
    resolver.add_type_handler(
        SingletonEffectiveHandler(
            backend.lifetimes, backend.instances, instance_factory
        )
    )
    resolver.add_type_handler(AbstractTypeHandler())
    resolver.add_type_handler(
        BuiltinsTypeHandler(my_builtins=[int, float, str, bytearray, bytes])
    )
    resolver.add_type_handler(NewInstanceHandler(instance_factory))
    return resolver


def _resolve_dependencies(backend: ConfigBackend, dependencies: List[object]):
    for dependency in dependencies:
        dependent_type = type(dependency)
        if dependent_type not in backend.dependencies.get_dependencies():
            raise TypeError(
                "no dependency was declared for type {dependent}".format(
                    dependent=type(dependency)
                )
            )
        backend.instances.set_instance(ConfigEntry(dependent_type), dependency)
        backend.dependencies.remove_dependency(dependent_type)

    if backend.dependencies.get_dependencies():
        raise TypeError(
            "no dependency were declared for the types  {dependency}".format(
                dependency=backend.dependencies.get_dependencies()
            )
        )
