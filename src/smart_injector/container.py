from typing import TypeVar, Type

T = TypeVar("T")


class StaticContainer:
    def get(self, a_type: Type[T]) -> T:
        return a_type()
