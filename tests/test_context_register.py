from smart_injector.register import ContextBased
from smart_injector.register import ContextRegister


class A:
    pass


class B:
    pass


class C:
    pass


class D:
    pass


def test_context_register():
    register = ContextRegister(lambda x: x.a_type)
    register.set(ContextBased(A, B), C)
    register.set(ContextBased(A, None), D)
    t1 = register.get(ContextBased(A, B))
    t2 = register.get(ContextBased(A, None))
    assert t1 is C
    assert t2 is D
    register.delete(ContextBased(A, B))
    t3 = register.get(ContextBased(A, B))
    assert t3 is D
    register.delete(ContextBased(A, None))
    t4 = register.get(ContextBased(A, B))
    assert t4 is A
