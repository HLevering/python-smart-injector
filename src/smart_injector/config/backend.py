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


class ConfigBackend:
    def __init__(self, default_lifetime: Lifetime):
        self._default_scope = default_lifetime
        self._bindings = ContextConfig[Callable[..., T]](lambda x: x.a_type)
        self._lifetimes = ContextConfig(lambda x: self._default_scope)
        self._factory_args = ContextConfig[Dict[str, Any]](lambda x: {})
        self._instances = ContextConfig[Optional[object]](lambda x: None)
        self._dependencies = {}  # type: Dict[Callable[..., T], None]

    def get_scope_visibility(self, what: TypeWithContext) -> ConfigVisibility:
        return self._lifetimes.get_visibility(what)

    def set_lifetime(self, what: TypeWithContext, lifetime: Lifetime):
        self._remove_lifetime_setting(what)
        if lifetime is not Lifetime._INTERNAL_DEFAULT:
            self._lifetimes.set(what, lifetime)

    def get_lifetime(self, what: TypeWithContext) -> Lifetime:
        return cast(Lifetime, self._lifetimes.get(what))

    def _remove_lifetime_setting(self, what: TypeWithContext):
        self._lifetimes.delete(what)

    def set_binding(self, what: TypeWithContext, to_type: Callable[..., S]):
        self._bindings.set(what, to_type)

    def get_binding(self, which: TypeWithContext) -> Callable[..., S]:
        return self._bindings.get(which)

    def set_factory_args(self, what: TypeWithContext, kwargs: Dict[str, Any]):
        self._factory_args.set(what, kwargs)

    def get_factory_args(self, what: TypeWithContext) -> Dict[str, Any]:
        return self._factory_args.get(what)

    def set_instance(self, what: TypeWithContext, instance: T):
        self._instances.set(what, instance)

    def has_instance(self, what: TypeWithContext) -> bool:
        return False if self._instances.get(what) is None else True

    def get_instance(self, what: TypeWithContext) -> T:
        return cast(T, self._instances.get(what))

    def is_singleton(self, what: TypeWithContext) -> bool:
        return True if self.get_lifetime(what) is Lifetime.SINGLETON else False

    def reset(self, what: TypeWithContext):
        self._bindings.delete(what)
        self._lifetimes.delete(what)
        self._factory_args.delete(what)
        self._instances.delete(what)
        self._dependencies.pop(what.a_type, None)

    def add_dependency(self, a_type: Callable[..., T]):
        if a_type not in self._dependencies:
            self._dependencies[a_type] = None

    def remove_dependency(self, a_type: Callable[..., T]):
        self._dependencies.pop(a_type, None)

    def get_dependencies(self) -> Dict[Callable[..., T], None]:
        return cast(Dict[Callable[..., T], None], self._dependencies)
