import inspect
from typing import Callable
from typing import Optional
from typing import Type
from typing import TypeVar

T = TypeVar("T")


def get_return_type(a_type: Callable[..., T]) -> Optional[Type[T]]:
    """returns the return type of a callable if it is available"""
    r_type = inspect.signature(a_type).return_annotation
    if r_type is inspect.Signature.empty:
        return None
    return r_type
