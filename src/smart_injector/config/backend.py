from collections import defaultdict
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import cast

from smart_injector.lifetime import Lifetime
from smart_injector.types import ConfigEntry


class ConfigVisibility(Enum):
    LOCAL = 0
    GLOBAL = 1


T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


class ContextConfig(Generic[U]):
    def __init__(self, default_factory: Callable[[ConfigEntry], U]):
        self._default_factory = default_factory
        self._default = {}  # type: Dict[Callable[..., T], U]
        self._with_context = cast(
            Dict[Callable[..., T], Dict[Callable[..., S], U]], defaultdict(dict)
        )

    def get_visibility(self, what: ConfigEntry) -> ConfigVisibility:
        if self.is_defined_locally(what):
            return ConfigVisibility.LOCAL
        else:
            return ConfigVisibility.GLOBAL

    def set(self, item: ConfigEntry, to_type: U):
        if item.where is None:
            self._default[item.a_type] = to_type
        else:
            self._with_context[item.where][item.a_type] = to_type

    def is_defined_locally(self, item: ConfigEntry) -> bool:
        if item.where is not None and item.a_type in self._with_context[item.where]:
            return True
        else:
            return False

    def get(self, item: ConfigEntry) -> U:
        if self.is_defined_locally(item):
            return self._with_context[cast(Callable[..., T], item.where)].get(
                item.a_type, self._default_factory(item)
            )
        return self._default.get(item.a_type, self._default_factory(item))

    def delete(self, item: ConfigEntry):
        if item.where is None:
            self._default.pop(item.a_type, cast(U, None))
        else:
            self._with_context[item.where].pop(item.a_type, cast(U, None))


class FactoryArgs:
    def __init__(self):
        self._config = ContextConfig[Dict[str, Any]](lambda x: {})

    def set_factory_args(self, what: ConfigEntry, kwargs: Dict[str, Any]):
        self._config.set(what, kwargs)

    def get_factory_args(self, what: ConfigEntry) -> Dict[str, Any]:
        return self._config.get(what)


class Instances:
    def __init__(self):
        self._config = ContextConfig[Optional[object]](lambda x: None)

    def set_instance(self, what: ConfigEntry, instance: T):
        self._config.set(what, instance)

    def has_instance(self, what: ConfigEntry) -> bool:
        return False if self._config.get(what) is None else True

    def get_instance(self, what: ConfigEntry) -> T:
        return cast(T, self._config.get(what))


class Bindings:
    def __init__(self):
        self._config = ContextConfig[Callable[..., T]](lambda x: x.a_type)

    def set_binding(self, what: ConfigEntry, to_type: Callable[..., S]):
        self._config.set(what, to_type)

    def get_binding(self, which: ConfigEntry) -> Callable[..., S]:
        return self._config.get(which)


class Lifetimes:
    def __init__(self, default_lifetime: Lifetime):
        self._config = ContextConfig[Callable[..., T]](
            lambda x: default_lifetime  # type: ignore
        )

    def is_singleton(self, what: ConfigEntry) -> bool:
        return (
            True
            if cast(Lifetime, self._config.get(what)) is Lifetime.SINGLETON
            else False
        )

    def set_lifetime(self, what: ConfigEntry, lifetime: Lifetime):
        self._remove_lifetime_setting(what)
        if lifetime is not Lifetime._INTERNAL_DEFAULT:
            self._config.set(what, lifetime)  # type: ignore

    def _remove_lifetime_setting(self, what: ConfigEntry):
        self._config.delete(what)

    def visibility(self, what: ConfigEntry) -> ConfigVisibility:
        return self._config.get_visibility(what)


class Dependencies:
    def __init__(self):
        self._dependencies = {}  # type: Dict[Callable[..., T], None]

    def add_dependency(self, a_type: Callable[..., T]):
        if a_type not in self._dependencies:
            self._dependencies[a_type] = None

    def remove_dependency(self, a_type: Callable[..., T]):
        self._dependencies.pop(a_type, None)

    def get_dependencies(self) -> Dict[Callable[..., T], None]:
        return cast(Dict[Callable[..., T], None], self._dependencies)


class ConfigBackend:
    """Simple container for all configuration classes"""

    def __init__(
        self,
        bindings: Bindings,
        lifetimes: Lifetimes,
        instances: Instances,
        factory_args: FactoryArgs,
        dependencies: Dependencies,
    ):
        self.bindings = bindings
        self.lifetimes = lifetimes
        self.instances = instances
        self.factory_args = factory_args
        self.dependencies = dependencies
