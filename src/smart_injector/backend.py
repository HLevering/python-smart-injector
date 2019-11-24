from typing import Callable
from typing import List
from typing import TypeVar
from typing import cast

from smart_injector.types import Handler
from smart_injector.types import LocalContext

T = TypeVar("T")
S = TypeVar("S")


class Resolver:
    def __init__(self):
        self._type_handlers = []  # type: List[Handler]

    def add_type_handler(self, handler: Handler):
        self._type_handlers.append(handler)

    def get_instance(self, a_type: Callable[..., T]) -> T:
        return self.get_new_instance(LocalContext(a_type, a_type, a_type))

    def get_new_instance(self, context: LocalContext) -> T:
        for handler in cast(
            List[Handler], self._type_handlers
        ):  # use list cast to surpress pylama List not used warning
            if handler.can_handle_type(context):
                return handler.handle(context)
        assert (
            False
        ), "should not reach this. you should have implemented a default handler"
