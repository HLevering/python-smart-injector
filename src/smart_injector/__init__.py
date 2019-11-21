__version__ = "0.0.3"

from typing import Type

from smart_injector.container import StaticContainer


def create_container(container: Type[StaticContainer]):
    return container(my_builtins=[int, float, str, bytearray, bytes])
