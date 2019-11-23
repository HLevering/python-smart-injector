from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import TypeVar

T = TypeVar("T")


class LocalContext:
    def __init__(self, a_type: Callable[..., T], base_type: Callable[..., T]):
        self.a_type = a_type
        self.base_type = base_type

    def get_new(self, a_type: Callable[..., T]) -> "LocalContext":
        return LocalContext(a_type, self.base_type)


class Handler(ABC):
    @abstractmethod
    def can_handle_type(self, context: LocalContext) -> bool:
        pass

    @abstractmethod
    def handle(self, context: LocalContext) -> T:
        pass
