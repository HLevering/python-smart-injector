from typing import List
from typing import Optional
from typing import Type

from smart_injector.config.backend import ConfigBackend
from smart_injector.config.backend import TypeWithContext
from smart_injector.config.user import Config
from smart_injector.container.container import StaticContainer
from smart_injector.lifetime import Lifetime
from smart_injector.resolver.handlers import AbstractTypeHandler
from smart_injector.resolver.handlers import BindingHandler
from smart_injector.resolver.handlers import BuiltinsTypeHandler
from smart_injector.resolver.handlers import DefaultTypeHandler
from smart_injector.resolver.handlers import InstanceHandler
from smart_injector.resolver.handlers import SingletonBaseTypeHandler
from smart_injector.resolver.handlers import SingletonEffectiveHandler
from smart_injector.resolver.resolver import Resolver


def create_container(
    container: Type[StaticContainer],
    default_lifetime=Lifetime.TRANSIENT,
    dependencies: Optional[List[object]] = None,
):
    if dependencies is None:
        dependencies = []
    register = ConfigBackend(default_lifetime)
    resolver = _create_resolver(register)
    new_container = container(resolver=resolver)
    new_container.configure(Config(register=register))
    _resolve_dependencies(register, dependencies)
    return new_container


def _create_resolver(register: ConfigBackend):
    resolver = Resolver()
    resolver.add_type_handler(InstanceHandler(register))
    resolver.add_type_handler(BindingHandler(resolver, register))
    resolver.add_type_handler(SingletonBaseTypeHandler(resolver, register))
    resolver.add_type_handler(SingletonEffectiveHandler(resolver, register))
    resolver.add_type_handler(AbstractTypeHandler())
    resolver.add_type_handler(
        BuiltinsTypeHandler(my_builtins=[int, float, str, bytearray, bytes])
    )
    resolver.add_type_handler(DefaultTypeHandler(resolver, register))
    return resolver


def _resolve_dependencies(register: ConfigBackend, dependencies: List[object]):
    for dependency in dependencies:
        dependent_type = type(dependency)
        if dependent_type not in register.get_dependencies():
            raise TypeError(
                "no dependency was declared for type {dependent}".format(
                    dependent=type(dependency)
                )
            )
        register.set_instance(TypeWithContext(dependent_type), dependency)
        register.remove_dependency(dependent_type)

    if register.get_dependencies():
        raise TypeError(
            "no dependency were declared for the types  {dependency}".format(
                dependency=register.get_dependencies()
            )
        )
