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
from smart_injector.types import TypeWithContext


class ConfigVisibility(Enum):
    LOCAL = 0
    GLOBAL = 1


T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


class ContextConfig(Generic[U]):
    def __init__(self, default_factory: Callable[[TypeWithContext], U]):
        self._default_factory = default_factory
        self._default = {}  # type: Dict[Callable[..., T], U]
        self._with_context = cast(
            Dict[Callable[..., T], Dict[Callable[..., S], U]], defaultdict(dict)
        )

    def get_visibility(self, what: TypeWithContext) -> ConfigVisibility:
        if self.is_defined_locally(what):
            return ConfigVisibility.LOCAL
        else:
            return ConfigVisibility.GLOBAL

    def set(self, item: TypeWithContext, to_type: U):
        if item.where is None:
            self._default[item.a_type] = to_type
        else:
            self._with_context[item.where][item.a_type] = to_type

    def is_defined_locally(self, item: TypeWithContext) -> bool:
        if item.where is not None and item.a_type in self._with_context[item.where]:
            return True
        else:
            return False

    def get(self, item: TypeWithContext) -> U:
        if self.is_defined_locally(item):
            return self._with_context[cast(Callable[..., T], item.where)].get(
                item.a_type, self._default_factory(item)
            )
        return self._default.get(item.a_type, self._default_factory(item))

    def delete(self, item: TypeWithContext):
        if item.where is None:
            self._default.pop(item.a_type, cast(U, None))
        else:
            self._with_context[item.where].pop(item.a_type, cast(U, None))


class FactoryArgs(ContextConfig[Dict[str, Any]]):
    def __init__(self):
        super().__init__(lambda x: {})

    def set_factory_args(self, what: TypeWithContext, kwargs: Dict[str, Any]):
        self.set(what, kwargs)

    def get_factory_args(self, what: TypeWithContext) -> Dict[str, Any]:
        return self.get(what)


class Instances(ContextConfig[Optional[object]]):
    def __init__(self):
        super().__init__(lambda x: None)

    def set_instance(self, what: TypeWithContext, instance: T):
        self.set(what, instance)

    def has_instance(self, what: TypeWithContext) -> bool:
        return False if self.get(what) is None else True

    def get_instance(self, what: TypeWithContext) -> T:
        return cast(T, self.get(what))


class Bindings(ContextConfig[Callable[..., T]]):
    def __init__(self):
        super().__init__(lambda x: x.a_type)

    def set_binding(self, what: TypeWithContext, to_type: Callable[..., S]):
        self.set(what, to_type)

    def get_binding(self, which: TypeWithContext) -> Callable[..., S]:
        return self.get(which)


class Lifetimes(ContextConfig[Callable[..., T]]):
    def __init__(self, default_lifetime: Lifetime):
        super().__init__(lambda x: default_lifetime)  # type: ignore

    def is_singleton(self, what: TypeWithContext) -> bool:
        return True if cast(Lifetime, self.get(what)) is Lifetime.SINGLETON else False

    def set_lifetime(self, what: TypeWithContext, lifetime: Lifetime):
        self._remove_lifetime_setting(what)
        if lifetime is not Lifetime._INTERNAL_DEFAULT:
            self.set(what, lifetime)

    def _remove_lifetime_setting(self, what: TypeWithContext):
        self.delete(what)

    def visibility(self, what: TypeWithContext) -> ConfigVisibility:
        return self.get_visibility(what)


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
