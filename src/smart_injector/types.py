from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Optional
from typing import TypeVar

T = TypeVar("T")


class TypeWithContext:
    def __init__(
        self, a_type: Callable[..., T], where: Optional[Callable[..., T]] = None
    ):
        self.a_type = a_type
        self.where = where


class DependencyContext:
    def __init__(
        self,
        a_type: Callable[..., T],
        base_type: Callable[..., T],
        where: Optional[Callable[..., T]],
    ):
        self.a_type = a_type
        self.base_type = base_type
        self.where = where

    def get_new_bind_context(self, a_type: Callable[..., T]) -> "DependencyContext":
        return DependencyContext(a_type, self.base_type, where=self.where)

    def get_new_dependency_context(
        self, a_type: Callable[..., T]
    ) -> "DependencyContext":
        return DependencyContext(a_type, self.a_type, where=self.where)

    def type_with_context(self) -> TypeWithContext:
        return TypeWithContext(self.a_type, self.where)

    def context_free_type(self) -> TypeWithContext:
        return TypeWithContext(self.a_type, where=None)

    def base_type_with_context(self) -> TypeWithContext:
        return TypeWithContext(self.base_type, self.where)

    def context_free_base_type(self) -> TypeWithContext:
        return TypeWithContext(self.base_type, where=None)


class Handler(ABC):
    @abstractmethod
    def can_handle_type(self, context: DependencyContext) -> bool:
        pass

    @abstractmethod
    def handle(self, context: DependencyContext) -> T:
        pass
