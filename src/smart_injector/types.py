from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Optional
from typing import TypeVar

T = TypeVar("T")


class ConfigEntry:
    def __init__(
        self, a_type: Callable[..., T], where: Optional[Callable[..., T]] = None
    ):
        self.a_type = a_type
        self.where = where


class ResolveRequest:
    def __init__(
        self,
        real_type: Callable[..., T],
        base_type: Callable[..., T],
        where: Optional[Callable[..., T]],
    ):
        self.real_type = real_type
        self.base_type = base_type
        self.where = where

    def new_request_with_same_origin(
        self, a_type: Callable[..., T]
    ) -> "ResolveRequest":
        return ResolveRequest(a_type, self.base_type, where=self.where)

    def get_new_dependency_context(self, a_type: Callable[..., T]) -> "ResolveRequest":
        return ResolveRequest(a_type, a_type, where=self.base_type)

    def local_config_entry(self) -> ConfigEntry:
        return ConfigEntry(self.real_type, self.where)

    def global_config_entry(self) -> ConfigEntry:
        return ConfigEntry(self.real_type, where=None)

    def local_base_config_entry(self) -> ConfigEntry:
        return ConfigEntry(self.base_type, self.where)

    def global_base_config_entry(self) -> ConfigEntry:
        return ConfigEntry(self.base_type, where=None)


class Handler(ABC):
    @abstractmethod
    def can_handle_type(self, request: ResolveRequest) -> bool:
        pass

    @abstractmethod
    def handle(self, request: ResolveRequest) -> T:
        pass
