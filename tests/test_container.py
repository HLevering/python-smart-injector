from abc import ABC
from abc import abstractmethod

import pytest  # type: ignore

from smart_injector import Lifetime
from smart_injector import StaticContainer
from smart_injector.config.backend import Bindings
from smart_injector.config.backend import ConfigBackend
from smart_injector.config.backend import Dependencies
from smart_injector.config.backend import FactoryArgs
from smart_injector.config.backend import Instances
from smart_injector.config.backend import Lifetimes
from smart_injector.config.user import Config
from smart_injector.container.factory import create_container
from smart_injector.resolver.resolver import Resolver


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


def test_container_resolves_chained_binding() -> None:
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
    lifetime = Lifetimes(Lifetime.TRANSIENT)
    instances = Instances()
    bindings = Bindings()
    factory_args = FactoryArgs()
    dependencies = Dependencies()
    backend = ConfigBackend(bindings, lifetime, instances, factory_args, dependencies)
    context = Config(backend)
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
    def configure(self, config: Config):
        config.set_lifetime(MySingleton, Lifetime.SINGLETON)
        config.set_lifetime(MyTransient, Lifetime.TRANSIENT)


def test_singleton_lifetimes() -> None:
    container = create_container(ScopeContainer)
    s1 = container.get(MySingleton)
    s2 = container.get(MySingleton)
    assert s1 is s2
    t1 = container.get(MyTransient)
    t2 = container.get(MyTransient)
    assert t1 is not t2


def test_default_lifetime_switched_to_singleton() -> None:
    container = create_container(StaticContainer, default_lifetime=Lifetime.SINGLETON)
    s1 = container.get(MySingleton)
    s2 = container.get(MySingleton)
    assert s1 is s2


def test_default_lifetime_is_transient() -> None:
    container = create_container(StaticContainer)
    t1 = container.get(MyTransient)
    t2 = container.get(MyTransient)
    assert t1 is not t2


class BindScopeContainer(StaticContainer):
    def configure(self, config: Config):
        config.bind(MyInterface, MyImplementation, lifetime=Lifetime.SINGLETON)


def test_bind_with_given_lifetime():
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
    def configure(self, config: Config):
        config.transient(Transient, a=42, b=10.0)


def test_transient_creates_transient_object_with_args():
    container = create_container(TransientProviderContainer)
    s1 = container.get(Transient)
    assert s1.a == 42
    assert s1.b == 10.0
    assert isinstance(s1.c, C)


class SingletonProviderContainer(StaticContainer):
    def configure(self, config: Config):
        config.singleton(Transient, a=42, b=10.0)


def test_singleton_creates_singleton_objects_with_args():
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
    def configure(self, config: Config):
        config.instance(MyInstance, MY_INSTANCE_INSTANCE)


def test_instance_returns_provided_intance():
    container = create_container(InstanceProviderContainer)
    instance = container.get(MyInstance)
    assert instance is MY_INSTANCE_INSTANCE


def get_my_Transient(a: int, c: C, b: float) -> Transient:
    return Transient(a, c, b)


class CallableProviderContainer(StaticContainer):
    def configure(self, config: Config):
        config.callable(get_my_Transient, a=42)


def test_callable_is_called_with_args_for_return_type_dependency():
    container = create_container(CallableProviderContainer)
    instance = container.get(Transient)
    assert instance.a == 42
    assert isinstance(instance.c, C)
    assert instance.b == 0.0


class BindToSingletonContainer(StaticContainer):
    def configure(self, config: Config):
        config.bind(MyInterface, MyImplementation)
        config.singleton(MyImplementation)


def test_lifetime_of_binded_type_is_singleton():
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
    def configure(self, config: Config):
        config.dependency(Dependecy)


def test_given_dependencies_are_used_for_resolution():
    dependency = Dependecy()
    container = create_container(DependencyContainer, dependencies=[dependency])
    dependent = container.get(NeedsDependency)
    assert dependent.dependent is dependency


class F(ABC):
    @abstractmethod
    def someting(self):
        pass


class F1(F):
    def someting(self):
        pass


class F2(F):
    def someting(self):
        pass


class UseF1:
    def __init__(self, f: F):
        self.f = f


class UseF2:
    def __init__(self, f: F):
        self.f = f


class ContextBindingContainer(StaticContainer):
    def configure(self, config: Config):
        config.bind(F, F1, where=UseF1)
        config.bind(F, F2, where=UseF2)


def test_binding_within_a_context():
    container = create_container(ContextBindingContainer)
    f1 = container.get(UseF1)
    f2 = container.get(UseF2)
    assert isinstance(f1.f, F1)
    assert isinstance(f2.f, F2)


class T:
    def __init__(self, a: int):
        self.a = a


class UseT1:
    def __init__(self, t: T):
        self.t = t


class UseT2:
    def __init__(self, t: T):
        self.t = t


class ContextTransientContainer(StaticContainer):
    def configure(self, config: Config):
        config.transient(T, a=1, where=UseT1)
        config.transient(T, a=2, where=UseT2)


def test_transient_within_a_context():
    container = create_container(ContextTransientContainer)
    t1 = container.get(UseT1)
    t2 = container.get(UseT2)
    assert t1.t.a == 1
    assert t2.t.a == 2


class ContextSingletonContainer(StaticContainer):
    def configure(self, config: Config):
        config.singleton(T, a=1, where=UseT1)
        config.singleton(T, a=2, where=UseT2)


def test_singleton_within_a_context():
    container = create_container(ContextSingletonContainer)
    t11 = container.get(UseT1)
    t12 = container.get(UseT1)
    t21 = container.get(UseT2)
    t22 = container.get(UseT2)
    assert t11.t.a == 1
    assert t11.t is t12.t
    assert t21.t.a == 2
    assert t21.t is t22.t


t1_instance = T(1)
t2_instance = T(2)


class ContextInstanceContainer(StaticContainer):
    def configure(self, config: Config):
        config.instance(T, t1_instance, where=UseT1)
        config.instance(T, t2_instance, where=UseT2)


def test_instance_within_a_context():
    container = create_container(ContextInstanceContainer)
    t1 = container.get(UseT1)
    t2 = container.get(UseT2)
    assert t1.t is t1_instance
    assert t2.t is t2_instance


def foo(a: int) -> T:
    return T(a)


class ContextCallableContainer(StaticContainer):
    def configure(self, config: Config):
        config.callable(foo, a=1, where=UseT1)
        config.callable(foo, a=2, where=UseT2)


def test_callable_within_a_context():
    container = create_container(ContextCallableContainer)
    t1 = container.get(UseT1)
    t2 = container.get(UseT2)
    assert t1.t.a == 1
    assert t2.t.a == 2


class UseT3:
    def __init__(self, t: T):
        self.t = t


class ContextScopeSettingContainer(StaticContainer):
    def configure(self, config: Config):
        config.callable(foo, a=1, where=UseT1)
        config.callable(foo, a=2, where=UseT2)
        config.set_lifetime(foo, Lifetime.SINGLETON, where=UseT2)
        config.callable(foo, a=2, where=UseT3, lifetime=Lifetime.SINGLETON)


def test_scope_setting_within_a_context():
    container = create_container(ContextScopeSettingContainer)
    t11 = container.get(UseT1)
    t12 = container.get(UseT1)
    t21 = container.get(UseT2)
    t22 = container.get(UseT2)
    assert t11.t.a == 1
    assert t11.t is not t12.t
    assert t21.t.a == 2
    assert t21.t is t22.t

    t31 = container.get(UseT3)
    t32 = container.get(UseT3)
    assert t31.t is t32.t


def test_resolver_raises_assertion_error_if_no_handler_is_found():
    resolver = Resolver()
    with pytest.raises(AssertionError):
        resolver.get_instance(int)


def test_give_a_non_registered_dependency_raises_type_error():
    with pytest.raises(TypeError):
        create_container(StaticContainer, dependencies=[5])


def test_define_a_dependency_without_providing_it_raises_typeerror():
    class Container(StaticContainer):
        def configure(self, config: Config):
            config.dependency(int)

    with pytest.raises(TypeError):
        create_container(Container)


def test_callable_which_returns_none_raises_typeerror():
    def foo():
        pass

    class Container(StaticContainer):
        def configure(self, config: Config):
            config.callable(foo)

    with pytest.raises(TypeError):
        create_container(Container)


class SB1:
    pass


class SB2(SB1):
    pass


class SB3(SB2):
    pass


class MySB:
    def __init__(self, sb: SB1):
        self.sb = sb


class StackedBindingScope(StaticContainer):
    def configure(self, config: Config):
        config.bind(SB1, SB2)
        config.set_lifetime(SB2, Lifetime.SINGLETON)
        config.bind(SB2, SB3)


def test_stacked_binding_uses_singleton_of_bound_to_object_first():
    container = create_container(StackedBindingScope)
    s1 = container.get(MySB)
    s2 = container.get(MySB)
    assert isinstance(s1.sb, SB3)
    assert s1.sb is not s2.sb


class MyArg:
    def __init__(self, arg1):
        self.arg1 = arg1


class ArgContainer(StaticContainer):
    def configure(self, config: Config):
        config.set_arguments(MyArg, arg1="foobar")


def test_provide_arguments_for_a_callable_container():
    container = create_container(ArgContainer)
    my_arg = container.get(MyArg)
    assert my_arg.arg1 == "foobar"
