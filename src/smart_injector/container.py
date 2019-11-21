import inspect
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import cast

T = TypeVar("T")
S = TypeVar("S")


class Context:
    def __init__(self):
        self._bindings = {}  # type: Dict[Callable[..., T], Callable[..., S]]

    def bind(self, a_type: Callable[..., T], to_type: Callable[..., S]):
        if a_type not in inspect.getmro(cast(type, to_type)):
            raise TypeError(
                "{to_type} must be a subclass of {a_type}".format(
                    to_type=to_type, a_type=a_type
                )
            )
        self._bindings[a_type] = to_type  # type: ignore

    def get_effective_binding(self, a_type: Callable[..., T]) -> Callable[..., S]:
        bound_type = self._bindings.get(a_type, a_type)
        if bound_type is a_type:
            return bound_type
        return self.get_effective_binding(bound_type)


class Handler(ABC):
    @abstractmethod
    def can_handle_type(self, a_type: Callable[..., T]) -> bool:
        pass

    @abstractmethod
    def handle(self, a_type: Callable[..., T], container: "StaticContainer") -> T:
        pass


class AbstractTypeHandler(Handler):
    def can_handle_type(self, a_type: Callable[..., T]) -> bool:
        return True if inspect.isabstract(a_type) else False

    def handle(self, a_type: Callable[..., T], container: "StaticContainer") -> T:
        raise TypeError("No binding for abstract base {0}".format(a_type))


class BuiltinsTypeHandler(Handler):
    def __init__(self, my_builtins: List[Type[Any]]):
        self._my_builtins = my_builtins

    def can_handle_type(self, a_type: Callable[..., T]) -> bool:
        return True if a_type in self._my_builtins else False

    def handle(self, a_type: Callable[..., T], container: "StaticContainer") -> T:
        return a_type()


class DefaultHandler(Handler):
    def can_handle_type(self, a_type: Callable[..., T]) -> bool:
        return True

    def handle(self, a_type: Callable[..., T], container: "StaticContainer") -> T:
        dependency_instances = container._build_dependencies(a_type)
        return a_type(**dependency_instances)


class StaticContainer:
    def __init__(self, context: Context, handlers: List[Handler]):
        self._context = context
        self._type_handlers = handlers

    def configure(self, context: Context):
        pass

    def _get_signature(self, a_type: Callable[..., T]) -> Dict[str, Type[Any]]:
        return {
            parameter.name: parameter.annotation
            for parameter in inspect.signature(a_type).parameters.values()
        }

    def _build_dependencies(self, a_type: Callable[..., T]) -> Dict[str, Type[Any]]:
        return {
            name: self.get(b_type)
            for name, b_type in self._get_signature(a_type).items()
        }

    def _default_construct(self, a_type: Callable[..., T]) -> T:
        return a_type()

    def get(self, a_type: Callable[..., T]) -> T:
        for handler in self._type_handlers:
            if handler.can_handle_type(self._context.get_effective_binding(a_type)):
                return handler.handle(cast(Callable[..., T], self._context.get_effective_binding(a_type)), self)
        assert (
            False
        ), "should not reach this. you should have implemented a default handler"
