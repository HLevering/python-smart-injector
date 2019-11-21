import pytest  # type: ignore

from smart_injector import StaticContainer
from smart_injector import create_container


class A:
    pass


def test_container_creates_simple_type():
    container = create_container(StaticContainer)
    my_int = container.get(A)
    assert isinstance(my_int, A)


@pytest.fixture
def container() -> StaticContainer:
    return create_container(StaticContainer)


class B:
    pass


class AB:
    def __init__(self, a: A, b: B):
        self.a = a
        self.b = b


def test_container_resolves_concrete_types(container: StaticContainer) -> None:
    ab = container.get(AB)
    assert isinstance(ab.a, A)
    assert isinstance(ab.b, B)


class C:
    pass


class ABC:
    def __init__(self, ab: AB, c: C):
        self.ab = ab
        self.c = c


def test_container_resolves_recursive_dependencies(container: StaticContainer) -> None:
    abc = container.get(ABC)
    assert isinstance(abc.ab.a, A)
    assert isinstance(abc.ab.b, B)
    assert isinstance(abc.c, C)


def test_container_resolves_builtins_to_default_values(
    container: StaticContainer
) -> None:
    my_int = container.get(int)
    assert my_int == 0
    my_float = container.get(float)
    assert my_float == 0.0
    my_str = container.get(str)
    assert my_str == ""
    my_bytes = container.get(bytes)
    assert my_bytes == b""
    my_bytes = container.get(bytearray)
    assert my_bytes == bytearray()


def a_func(a: A, b: B, abc: ABC) -> C:
    return C()


def test_resolve_a_function(container: StaticContainer) -> None:
    my_result = container.get(a_func)
    assert isinstance(my_result, C)



