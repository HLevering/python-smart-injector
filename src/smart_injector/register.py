from collections import defaultdict
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import cast

from smart_injector.scope import Scope
from smart_injector.types import ContextBased


class ScopeVisibility(Enum):
    LOCAL = 0
    GLOBAL = 1


T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")


class ContextRegister(Generic[U]):
    def __init__(self, default_factory: Callable[[ContextBased], U]):
        self._default_factory = default_factory
        self._default = {}  # type: Dict[Callable[..., T], U]
        self._with_context = cast(
            Dict[Callable[..., T], Dict[Callable[..., S], U]], defaultdict(dict)
        )

    def get_visibility(self, what: ContextBased) -> ScopeVisibility:
        if self.is_defined_locally(what):
            return ScopeVisibility.LOCAL
        else:
            return ScopeVisibility.GLOBAL

    def set(self, item: ContextBased, to_type: U):
        if item.where is None:
            self._default[item.a_type] = to_type
        else:
            self._with_context[item.where][item.a_type] = to_type

    def is_defined_locally(self, item: ContextBased) -> bool:
        if item.where is not None and item.a_type in self._with_context[item.where]:
            return True
        else:
            return False

    def get(self, item: ContextBased) -> U:
        if self.is_defined_locally(item):
            return self._with_context[cast(Callable[..., T], item.where)].get(
                item.a_type, self._default_factory(item)
            )
        return self._default.get(item.a_type, self._default_factory(item))

    def delete(self, item: ContextBased):
        if item.where is None:
            self._default.pop(item.a_type, cast(U, None))
        else:
            self._with_context[item.where].pop(item.a_type, cast(U, None))


class Register:
    def __init__(self, default_scope: Scope):
        self._default_scope = default_scope
        self._bindings = ContextRegister[Callable[..., T]](lambda x: x.a_type)
        self._scopes = ContextRegister(lambda x: self._default_scope)
        self._factory_args = ContextRegister[Dict[str, Any]](lambda x: {})
        self._instances = ContextRegister[Optional[object]](lambda x: None)
        self._dependencies = {}  # type: Dict[Callable[..., T], None]

    def get_scope_visibility(self, what: ContextBased) -> ScopeVisibility:
        return self._scopes.get_visibility(what)

    def set_scope(self, what: ContextBased, scope: Scope):
        self._remove_scope_setting(what)
        if scope is not Scope._INTERNAL_DEFAULT:
            self._scopes.set(what, scope)

    def get_scope(self, what: ContextBased) -> Scope:
        return cast(Scope, self._scopes.get(what))

    def _remove_scope_setting(self, what: ContextBased):
        self._scopes.delete(what)

    def set_binding(self, what: ContextBased, to_type: Callable[..., S]):
        self._bindings.set(what, to_type)

    def get_binding(self, which: ContextBased) -> Callable[..., S]:
        return self._bindings.get(which)

    def set_factory_args(self, what: ContextBased, kwargs: Dict[str, Any]):
        self._factory_args.set(what, kwargs)

    def get_factory_args(self, what: ContextBased) -> Dict[str, Any]:
        return self._factory_args.get(what)

    def set_instance(self, what: ContextBased, instance: T):
        self._instances.set(what, instance)

    def has_instance(self, what: ContextBased) -> bool:
        return False if self._instances.get(what) is None else True

    def get_instance(self, what: ContextBased) -> T:
        return cast(T, self._instances.get(what))

    def is_singleton(self, what: ContextBased) -> bool:
        return True if self.get_scope(what) is Scope.SINGLETON else False

    def reset(self, what: ContextBased):
        self._bindings.delete(what)
        self._scopes.delete(what)
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
