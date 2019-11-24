from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Optional
from typing import TypeVar

T = TypeVar("T")


class LocalContext:
    def __init__(
        self,
        a_type: Callable[..., T],
        base_type: Callable[..., T],
        where: Optional[Callable[..., T]],
    ):
        self.a_type = a_type
        self.base_type = base_type
        self.where = where

    def get_new_bound(self, a_type: Callable[..., T]) -> "LocalContext":
        return LocalContext(a_type, self.base_type, where=self.where)

    def get_new_unbound(self, a_type: Callable[..., T]) -> "LocalContext":
        return LocalContext(a_type, self.a_type, where=self.where)


class Handler(ABC):
    @abstractmethod
    def can_handle_type(self, context: LocalContext) -> bool:
        pass

    @abstractmethod
    def handle(self, context: LocalContext) -> T:
        pass


class ContextBased:
    def __init__(
        self, a_type: Callable[..., T], where: Optional[Callable[..., T]] = None
    ):
        self.a_type = a_type
        self.where = where
