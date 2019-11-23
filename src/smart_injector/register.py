from typing import Any
from typing import Callable
from typing import Dict
from typing import TypeVar
from typing import cast

from smart_injector.scope import Scope

T = TypeVar("T")
S = TypeVar("S")


class Register:
    def __init__(self, default_scope: Scope):
        self._default_scope = default_scope
        self._bindings = {}  # type: Dict[Callable[..., T], Callable[..., S]]
        self._scopes = {}  # type: Dict[Callable[..., T], Scope]
        self._factory_args = {}  # type: Dict[Callable[..., T], Dict[str, Any]]
        self._instances = {}  # type: Dict[Callable[..., T], object]
        self._callables = {}  # type: Dict[Callable[..., T], object]
        self._dependencies = {}  # type: Dict[Callable[..., object], None]

    def set_scope(self, a_type: Callable[..., T], scope: Scope):
        self._remove_scope_setting(a_type)
        if scope is not Scope.DEFAULT:
            self._scopes[a_type] = scope

    def get_scope(self, a_type: Callable[..., T]) -> Scope:
        return self._scopes.pop((a_type), self._default_scope)

    def _remove_scope_setting(self, a_type: Callable[..., T]):
        self._scopes.pop(a_type, None)

    def set_binding(self, a_type: Callable[..., T], to_type: Callable[..., S]):
        self._bindings[a_type] = to_type  # type: ignore

    def get_binding(self, a_type: Callable[..., T]) -> Callable[..., S]:
        return self._bindings.get(a_type, a_type)

    def set_factory_args(self, a_type: Callable[..., T], kwargs: Dict[str, Any]):
        self._factory_args[a_type] = kwargs

    def get_factory_args(self, a_type: Callable[..., T]) -> Dict[str, Any]:
        return self._factory_args.get(a_type, {})

    def set_instance(self, a_type: Callable[..., T], instance: T):
        self._instances[a_type] = instance

    def has_instance(self, a_type: Callable[..., T]) -> bool:
        return True if a_type in self._instances else False

    def get_instance(self, a_type: Callable[..., T]) -> T:
        return cast(T, self._instances.get(a_type))

    def is_singleton(self, a_type: Callable[..., T]) -> bool:
        return True if self.get_scope(a_type) is Scope.SINGLETON else False

    def reset(self, a_type: Callable[..., T]):
        self._bindings.pop(a_type, None)
        self._scopes.pop(a_type, None)
        self._factory_args.pop(a_type, None)
        self._instances.pop(a_type, None)
        self._callables.pop(a_type, None)
        self._dependencies.pop(a_type, None)

    def add_dependency(self, a_type: Callable[..., T]):
        if a_type not in self._dependencies:
            self._dependencies[a_type] = None

    def remove_dependency(self, a_type: Callable[..., T]):
        self._dependencies.pop(a_type, None)

    def get_dependencies(self) -> Dict[Callable[..., T], None]:
        return cast(Dict[Callable[..., T], None], self._dependencies)
