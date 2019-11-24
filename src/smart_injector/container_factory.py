from typing import List
from typing import Optional
from typing import Type

from smart_injector.backend import Resolver
from smart_injector.container import StaticContainer
from smart_injector.handlers import AbstractTypeHandler
from smart_injector.handlers import BindingHandler
from smart_injector.handlers import BuiltinsTypeHandler
from smart_injector.handlers import DefaultTypeHandler
from smart_injector.handlers import InstanceHandler
from smart_injector.handlers import SingletonBaseHandler
from smart_injector.handlers import SingletonEffectiveHandler
from smart_injector.register import ContextBased
from smart_injector.register import Register
from smart_injector.scope import Scope
from smart_injector.user_context import Context


def create_container(
    container: Type[StaticContainer],
    default_scope=Scope.TRANSIENT,
    dependencies: Optional[List[object]] = None,
):
    if dependencies is None:
        dependencies = []
    register = Register(default_scope)
    resolver = _create_resolver(register)
    new_container = container(resolver=resolver)
    new_container.configure(Context(register=register))
    _resolve_dependencies(register, dependencies)
    return new_container


def _create_resolver(register: Register):
    resolver = Resolver()
    resolver.add_type_handler(InstanceHandler(register))
    resolver.add_type_handler(BindingHandler(resolver, register))
    resolver.add_type_handler(SingletonBaseHandler(resolver, register))
    resolver.add_type_handler(SingletonEffectiveHandler(resolver, register))
    resolver.add_type_handler(AbstractTypeHandler())
    resolver.add_type_handler(
        BuiltinsTypeHandler(my_builtins=[int, float, str, bytearray, bytes])
    )
    resolver.add_type_handler(DefaultTypeHandler(resolver, register))
    return resolver


def _resolve_dependencies(register: Register, dependencies: List[object]):
    for dependency in dependencies:
        dependent_type = type(dependency)
        if dependent_type not in register.get_dependencies():
            raise TypeError(
                "no dependency was declared for type {dependent}".format(
                    dependent=type(dependency)
                )
            )
        register.set_instance(ContextBased(dependent_type), dependency)
        register.remove_dependency(dependent_type)

    if register.get_dependencies():
        raise TypeError(
            "no dependency were declared for the types  {dependency}".format(
                dependency=register.get_dependencies()
            )
        )
