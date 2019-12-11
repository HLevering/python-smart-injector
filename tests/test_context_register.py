from smart_injector.config.backend import ConfigEntry
from smart_injector.config.backend import ContextConfig


class A:
    pass


class B:
    pass


class C:
    pass


class D:
    pass


def test_context_register():
    register = ContextConfig(lambda x: x.a_type)
    register.set(ConfigEntry(A, B), C)
    register.set(ConfigEntry(A, None), D)
    t1 = register.get(ConfigEntry(A, B))
    t2 = register.get(ConfigEntry(A, None))
    assert t1 is C
    assert t2 is D
    register.delete(ConfigEntry(A, B))
    t3 = register.get(ConfigEntry(A, B))
    assert t3 is D
    register.delete(ConfigEntry(A, None))
    t4 = register.get(ConfigEntry(A, B))
    assert t4 is A
