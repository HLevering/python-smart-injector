from abc import ABC
from abc import abstractmethod

import pytest  # type: ignore

from smart_injector import StaticContainer
from smart_injector import create_container
from smart_injector.container import Context


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


class MyABC:
    def __init__(self, ab: AB, c: C):
        self.ab = ab
        self.c = c


def test_container_resolves_recursive_dependencies(container: StaticContainer) -> None:
    abc = container.get(MyABC)
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


def a_func(a: A, b: B, abc: MyABC) -> C:
    return C()


def test_resolve_a_function(container: StaticContainer) -> None:
    my_result = container.get(a_func)
    assert isinstance(my_result, C)


class MyInterface(ABC):
    @abstractmethod
    def foobar(self):
        pass


def test_given_an_abstract_base_type_raises_typeerror(
    container: StaticContainer
) -> None:
    with pytest.raises(TypeError) as e:
        container.get(MyInterface)
    assert "No binding for abstract base" in str(e)
    assert "MyInterface" in str(e)


class MyImplementation(MyInterface):
    def foobar(self):
        pass


class BindContainer(StaticContainer):
    def configure(self, ctx):
        ctx.bind(MyInterface, MyImplementation)


def test_given_a_binding_for_interface_creates_specified_concrete_type() -> None:
    container = create_container(BindContainer)
    concrete_object = container.get(MyInterface)
    assert isinstance(concrete_object, MyImplementation)


class H1(ABC):
    @abstractmethod
    def foobar(self):
        pass


class H2(H1):
    pass


class H3(H2):
    def foobar(self):
        pass


class BindHierarchyContainer(StaticContainer):
    def configure(self, ctx):
        ctx.bind(H1, H2)
        ctx.bind(H2, H3)


def test_bind_hierarchy() -> None:
    container = create_container(BindHierarchyContainer)
    concrete_object = container.get(H1)
    assert isinstance(concrete_object, H3)


class MyBaseClass(ABC):
    @abstractmethod
    def foobar(self):
        pass


class NotASubclass:
    pass


def test_bind_a_non_subclass_raises_typeerror() -> None:
    context = Context()
    with pytest.raises(TypeError) as e:
        context.bind(MyBaseClass, NotASubclass)
    assert "{NotASubclass} must be a subclass of {MyBaseClass}".format(
        NotASubclass=NotASubclass, MyBaseClass=MyBaseClass
    ) in str(e)
