from enum import Enum


class Lifetime(Enum):
    """Specifies the lifetime for objects created by the container

    :Lifetime.SINGLETON: :py:meth:`smart_injector.StaticContainer.get` returns the same every instance on every call
    :Lifetime.TRANSIENT: :py:meth:`smart_injector.StaticContainer.get` returns a new instance on every call
    """

    SINGLETON = 0
    TRANSIENT = 1
    _INTERNAL_DEFAULT = 2
