from smart_injector.config.backend import ContextConfig
from smart_injector.config.backend import TypeWithContext


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
    register.set(TypeWithContext(A, B), C)
    register.set(TypeWithContext(A, None), D)
    t1 = register.get(TypeWithContext(A, B))
    t2 = register.get(TypeWithContext(A, None))
    assert t1 is C
    assert t2 is D
    register.delete(TypeWithContext(A, B))
    t3 = register.get(TypeWithContext(A, B))
    assert t3 is D
    register.delete(TypeWithContext(A, None))
    t4 = register.get(TypeWithContext(A, B))
    assert t4 is A
