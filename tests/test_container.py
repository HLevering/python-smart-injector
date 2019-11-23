from abc import ABC
from abc import abstractmethod

import pytest  # type: ignore

from smart_injector import Scope
from smart_injector import StaticContainer
from smart_injector.container_factory import create_container
from smart_injector.register import Register
from smart_injector.user_context import Context


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
    register = Register(Scope.TRANSIENT)
    context = Context(register)
    with pytest.raises(TypeError) as e:
        context.bind(MyBaseClass, NotASubclass)
    assert "{NotASubclass} must be a subclass of {MyBaseClass}".format(
        NotASubclass=NotASubclass, MyBaseClass=MyBaseClass
    ) in str(e)


class MySingleton:
    pass


class MyTransient:
    pass


class ScopeContainer(StaticContainer):
    def configure(self, context: Context):
        context.set_scope(MySingleton, Scope.SINGLETON)
        context.set_scope(MyTransient, Scope.TRANSIENT)


def test_scopes() -> None:
    container = create_container(ScopeContainer)
    s1 = container.get(MySingleton)
    s2 = container.get(MySingleton)
    assert s1 is s2
    t1 = container.get(MyTransient)
    t2 = container.get(MyTransient)
    assert t1 is not t2


def test_default_scope_switched_to_singleton() -> None:
    container = create_container(StaticContainer, default_scope=Scope.SINGLETON)
    s1 = container.get(MySingleton)
    s2 = container.get(MySingleton)
    assert s1 is s2


def test_default_scope_is_transient() -> None:
    container = create_container(StaticContainer)
    t1 = container.get(MyTransient)
    t2 = container.get(MyTransient)
    assert t1 is not t2


class BindScopeContainer(StaticContainer):
    def configure(self, context: Context):
        context.bind(MyInterface, MyImplementation, scope=Scope.SINGLETON)


def test_bind_scope():
    container = create_container(BindScopeContainer)
    s1 = container.get(MyInterface)
    s2 = container.get(MyInterface)
    assert s1 is s2


class Transient:
    def __init__(self, a: int, c: C, b: float):
        self.a = a
        self.b = b
        self.c = c


class TransientProviderContainer(StaticContainer):
    def configure(self, context: Context):
        context.transient(Transient, a=42, b=10.0)


def test_transient_provider():
    container = create_container(TransientProviderContainer)
    s1 = container.get(Transient)
    assert s1.a == 42
    assert s1.b == 10.0
    assert isinstance(s1.c, C)


class SingletonProviderContainer(StaticContainer):
    def configure(self, context: Context):
        context.singleton(Transient, a=42, b=10.0)


def test_singleton_provider():
    container = create_container(SingletonProviderContainer)
    s1 = container.get(Transient)
    s2 = container.get(Transient)
    assert s1.a == 42
    assert s1.b == 10.0
    assert s1 is s2


class MyInstance:
    pass


MY_INSTANCE_INSTANCE = MyInstance()


class InstanceProviderContainer(StaticContainer):
    def configure(self, context: Context):
        context.instance(MyInstance, MY_INSTANCE_INSTANCE)


def test_instance_provider():
    container = create_container(InstanceProviderContainer)
    instance = container.get(MyInstance)
    assert instance is MY_INSTANCE_INSTANCE


def get_my_Transient(a: int, c: C, b: float) -> Transient:
    return Transient(a, c, b)


class CallableProviderContainer(StaticContainer):
    def configure(self, context: Context):
        context.callable(get_my_Transient, a=42)


def test_callable_provider():
    container = create_container(CallableProviderContainer)
    instance = container.get(Transient)
    assert instance.a == 42
    assert isinstance(instance.c, C)
    assert instance.b == 0.0


class BindToSingletonContainer(StaticContainer):
    def configure(self, context: Context):
        context.bind(MyInterface, MyImplementation)
        context.singleton(MyImplementation)


def test_bind_to_singleton():
    container = create_container(BindToSingletonContainer)
    s1 = container.get(MyInterface)
    s2 = container.get(MyInterface)
    assert s1 is s2


class Dependecy:
    pass


class NeedsDependency:
    def __init__(self, dependet: Dependecy):
        self.dependent = dependet


class DependencyContainer(StaticContainer):
    def configure(self, context: Context):
        context.dependency(Dependecy)


def test_dependency_container():
    dependency = Dependecy()
    container = create_container(DependencyContainer, dependencies=[dependency])
    dependent = container.get(NeedsDependency)
    assert dependent.dependent is dependency
