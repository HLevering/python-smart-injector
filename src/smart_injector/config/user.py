import inspect
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import cast

from smart_injector.config.backend import ConfigBackend
from smart_injector.config.backend import FactoryArg
from smart_injector.config.backend import ValueArg
from smart_injector.lifetime import Lifetime
from smart_injector.types import ConfigEntry
from smart_injector.utility import get_return_type

T = TypeVar("T")
S = TypeVar("S")

Where = Optional[Type[T]]


def is_base_class(base: Callable[..., T], subclass: Callable[..., S]) -> bool:
    if base in inspect.getmro(cast(type, subclass)):
        return True
    return False


def ensure_subclass(a_type: Callable[..., T], to_type: Optional[Callable[..., S]]):
    if to_type is None or not is_base_class(a_type, to_type):
        raise TypeError(
            "{to_type} must be a subclass of {a_type}".format(
                to_type=to_type, a_type=a_type
            )
        )


def ensure_binding(a_type: Callable[..., T], to_type: Callable[..., S]):
    if inspect.isclass(to_type):
        ensure_subclass(a_type, to_type)
    elif callable(a_type):
        if get_return_type(to_type) is None:
            raise TypeError(
                "type annotation for callable {to_type} is None or is missing".format(
                    to_type=to_type
                )
            )
        ensure_subclass(a_type, get_return_type(to_type))
    else:
        raise TypeError("{to_type} must be callable".format(to_type=to_type))


class Config:
    """Used by the user to configure DI container injection behaviour"""

    def __init__(self, backend: ConfigBackend):
        """
        Users should not directly create a config by invoking this contructor. Instead use
        :py:meth:`smart_injector.create_container`

        """
        self._backend = backend

    def bind(
        self, a_type: Callable[..., T], to_type: Callable[..., S], where: Where = None
    ):
        """Specify a binding. Whenever an object of type a_type is required, then an object of type to_type will be provided.
        For example you can configure, which concrete class shall be used for an abstract base class

        :param a_type: will be replaced by to_type
        :param to_type: will be used when an object of type a_type is required. to_type must be a subclass of a_type
        :param where:
        :param kwargs:

        :return:
        """
        ensure_binding(a_type, to_type)
        self._backend.bindings.set_binding(ConfigEntry(a_type, where), to_type)

    def lifetime(
        self, a_type: Callable[..., T], lifetime: Lifetime, where: Where = None
    ):
        """
        Specify the lifetime for an object of type `T`. See :py:meth:`smart_injector.Lifetime`

        :param a_type:
        :param lifetime:
        :param where:
        :return: None

        """
        self._backend.lifetimes.set_lifetime(ConfigEntry(a_type, where), lifetime)

    def instance(self, a_type: Callable[..., T], instance: T, where: Where = None):
        """
        set an instance of type `T` which is returned whenever an object of type `T` is requested

        :param a_type:
        :param instance:
        :param where:
        :return:

        """
        if not isinstance(instance, cast(Type[T], a_type)):
            raise TypeError(
                "{instance} is not an instance of type {a_type}".format(
                    instance=instance, a_type=a_type
                )
            )
        self._backend.instances.set_instance(ConfigEntry(a_type, where), instance)

    def dependency(self, a_type: Callable[..., T]):
        """
        declare that `T` is a dependency for the container. When creating the container with :py:meth:`smart_injector.create_container`
        an instance must be provided for every dependency which was declared.

        :param a_type:
        :return:

        """
        self._backend.dependencies.add_dependency(a_type)

    def arguments(self, a_type: Callable[..., T], where: Where = None, **kwargs: Any):
        """
        When creating an object of type `T`, the provided arguments will be inserted in `T`'s constructor (if it is a class) or
        a_type will be called with this arguments if it  is a function.

        :param a_type:
        :param where:
        :param kwargs:
        :return:

        .. Note:: Only keyword arguments are supported
        """
        ensure_arguments(a_type, kwargs)
        self._backend.factory_args.set_factory_args(
            ConfigEntry(a_type, where),
            {name: ValueArg(value) for name, value in kwargs.items()},
        )

    def arg_factory(
        self, a_type: Callable[..., T], where: Where = None, **kwargs: Callable[..., S]
    ):
        """
        In difference to :py:meth:`.arguments`:
        Instead of providing a value for `parameter` directly, `factory` is called
        to get the value for the parameter.

        :param a_type:
        :param where:
        :param kwargs:
        :return:
        """
        for parameter, factory in kwargs.items():
            ensure_parameter(a_type, parameter)
            self._backend.factory_args.set_factory_args(
                ConfigEntry(a_type, where), {parameter: FactoryArg(factory)}
            )


def ensure_arguments(a_type: Callable[..., T], kwargs: Dict[str, Any]):
    for parameter in kwargs:
        ensure_parameter(a_type, parameter)


def ensure_parameter(a_type: Callable[..., T], parameter: str):
    if not has_parameter(a_type, parameter):
        raise TypeError(
            "parameter {parameter} not expected for type {a_type}".format(
                parameter=parameter, a_type=a_type
            )
        )


def has_parameter(a_type: Callable[..., T], parameter: str) -> bool:
    expected_parameters = inspect.signature(a_type).parameters.keys()
    return True if parameter in expected_parameters else False
