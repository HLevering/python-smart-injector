__version__ = "0.0.3"

from typing import Type

from smart_injector.container import AbstractTypeHandler as _AbstractTypeHandler
from smart_injector.container import BuiltinsTypeHandler as _BuiltinsTypeHandler
from smart_injector.container import Context as _Context
from smart_injector.container import DefaultHandler as _DefaultHandler
from smart_injector.container import StaticContainer


def create_container(container: Type[StaticContainer]):
    context = _Context()
    new_container = container(
        context=context,
        handlers=[
            _AbstractTypeHandler(),
            _BuiltinsTypeHandler(my_builtins=[int, float, str, bytearray, bytes]),
            _DefaultHandler(),
        ],
    )
    new_container.configure(context)
    return new_container
