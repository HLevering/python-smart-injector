=====
Usage
=====

To use Smart Injector in a project::

	import smart_injector


Basic example:
==============

.. testcode::

    from smart_injector import create_container, StaticContainer

    class A:
        pass
    
    class B:
        def __init__(self, a: A):
            self.a = a
                
    container = create_container(StaticContainer)
    b = container.get(B)
    print(isinstance(b.a, A))

.. testoutput::

    True

Smart-injector relies on type annotations to resolve dependencies. Therefore type annotated code is a must have, if you want to use smart-injector efficiently. For many cases smart-injecot can resolve dependencies automatically. However, there are some limitations for the automatic depenendency resolving mechanism.

- dependencies on abstract types
- dependencies on builtin types
- explicitly provide arguments
- setting lifetime of a dependency
- set dependency to a specific instance


These cases need explicitly configuration. We will cover container configuration in the next sections.


Dependencies on abstract types
==============================

Abstract types (classes that inherit from abc.ABC and have abstractmethods) cannot be instantiated directly. There for it is impossible for smart-injector to resolve these kind of dependencies. An explicit binding of an abstract class to a concret class must be configured
However, configuration can be done quite easily:

.. testcode::

    from abc import ABC, abstractmethod

    class A(ABC):
        @abstractmethod
        def do(self):
            pass
    
    class ConcretA(A):
        def do(self):
            print("Hello")

    from smart_injector import Config # not needed but lets you type annotate your configure method

    #create your own container class by inheriting from StaticContainer
    class MyContainer(StaticContainer):
        # override configure method
        def configure(self, config: Config):
            # use config's bind method to bind A to ConcretA
            config.bind(A, ConcretA)
            # now everytime when there is a dependency on A then ConcretA will be injected

    # create an instance of your new defined container            
    container = create_container(MyContainer)
    a = container.get(A)
    a.do()


.. testoutput::

    Hello


Binding is not restricted to abstract classes. You can bind type A to type B as long as type B is a subclass of type A. Moreover, it is possible to chain bindings. Let's take the last example and add one more class


.. testcode::

    from abc import ABC, abstractmethod

    class A(ABC):
        @abstractmethod
        def do(self):
            pass
    
    class ConcretA(A):
        def do(self):
            print("Hello")

    class ConcretB(ConcretA):
        def do(self):
            print("World")

    class MyContainer(StaticContainer):
        # override configure method
        def configure(self, config: Config):
            config.bind(A, ConcretA)
            config.bind(ConcretA, ConcretB)
            # now everytime when there is a dependency on A then ConcretB will be injected

    # create an instance of your new defined container            
    container = create_container(MyContainer)
    a = container.get(A)
    a.do()


.. testoutput::

    World

Dependencies on builtin types
=============================

Dependencies on builtin types are default constructed by default.

.. testcode::

    container = create_container(StaticContainer)
    print(container.get(int))
    print(container.get(float))
    print(container.get(str))
    print(container.get(bytes))
    print(container.get(bytearray))


.. testoutput::

    0
    0.0
    
    b''
    bytearray(b'')


Often this is not what you want. Therefore you have to explicitly provide arguments.


Explicitly provide arguments
============================

You can provide arguments explicitly by configuring your container to do so


.. testcode::

    class MyClass:
        def __init__(self, a: str, b: int, c: float):
            self.a = a
            self.b = b
            self.c = c

    class MyContainer(StaticContainer):
        def configure(self, config: Config):
            # use config's set_arguments method to provide some arguments
            config.set_arguments(MyClass, a="hello", b=42, c=1.0)
            # now everytime when there is a dependency on MyClass then MyClass(a="hello", b=42, c=1.0) will be inserted

    container = create_container(MyContainer)
    a = container.get(MyClass)
    print(a.a)
    print(a.b)
    print(a.c)


.. testoutput::

    hello
    42
    1.0


If arguments are provided explicitly, it is not necessary to provide all arguments. Arguments which are not specified, are resolved by smart-injector.

.. testcode::

    class Foo:
        pass

    class MyClass:
        def __init__(self, a: str, foo: Foo, c: float):
            self.a = a
            self.foo = foo
            self.c = c

    class MyContainer(StaticContainer):
        def configure(self, config: Config):
            # use config's set_arguments method to provide some arguments
            config.set_arguments(MyClass, a="hello", c=1.0)
            # now everytime when there is a dependency on MyClass then MyClass(a="hello", b=42, c=1.0) will be inserted

    container = create_container(MyContainer)
    a = container.get(MyClass)
    print(a.a)
    print(isinstance(a.foo, Foo))
    print(a.c)


.. testoutput::

    hello
    True
    1.0


By explicitly providing arguments it is also possible to resolve dependencies without type annotations without type annotations.
 
 .. testcode::

    class MyClass:
        def __init__(self, a):
            self.a = a

    class MyContainer(StaticContainer):
        def configure(self, config: Config):
            # use config's set_arguments method to provide some arguments
            config.set_arguments(MyClass, a="hello")
            # now everytime when there is a dependency on MyClass then MyClass(a="hello", b=42, c=1.0) will be inserted

    container = create_container(MyContainer)
    a = container.get(MyClass)
    print(a.a)

.. testoutput::

    hello

.. note:: At the moment only keyword arguments can be provided with set_arguments. Moreover, you cannot provide the keyword argument "where" which is used to specify arguments in a specific context


Setting dependency's lifetime
=============================

By default all injected objects have a transient lifetime. That means, that everytime when an object is needed a new instance of that object is created.


.. testcode::

    class A:
        pass

    class B:
        pass

    from smart_injector import Lifetime

    class MyContainer(StaticContainer):
        def configure(self, config: Config):
            # use config's set_lifetime method to specify an objects lifetime
            config.set_lifetime(A, lifetime=Lifetime.SINGLETON)
            # now there will be only one object of type A, which will be inserted wherever an object A is needed
            config.set_lifetime(B, lifetime=Lifetime.TRANSIENT)
            # everytime a new object B is created. This is the default behaviour for all types

    container = create_container(MyContainer)
    a1 = container.get(A)
    a2 = container.get(A)
    b1 = container.get(B)
    b2 = container.get(B)
    print(a1 is a2)
    print(b1 is b2)

.. testoutput::

    True
    False


It is possible to override the default lifetime for objects created by a container. This must be done when the container is created

.. testcode::

    class A:
        pass


    from smart_injector import Lifetime

    container = create_container(StaticContainer, default_lifetime=Lifetime.SINGLETON)
    a1 = container.get(A)
    a2 = container.get(A)
    print(a1 is a2)

.. testoutput::

    True


Specify a specific instance
###########################

If you want, that a specific instance is used for a type you can do that to.


.. testcode::

    class A:
        def __init__(self, a: str):
            self.a = a

    my_a = A("foo")

    class MyContainer(StaticContainer):
        def configure(self, config: Config):
            # use config's instance method to specify that a particular instance shall be used
            config.instance(A, my_a)
            # every time an object of type A is needed, the instance my_a will be returned

    container = create_container(MyContainer)
    a1 = container.get(A)
    print(a1 is my_a)

.. testoutput::

    True


Specify a callable
###########################


You can provide a callable during configuration. The return_type is determined by the container. When an object of the return type is needed, the callable is invoked to create an object of type 'return_type'. The dependencies of the callable can be explicitly provided as arguments or are determined by the container.


.. testcode::

    class A:
        def __init__(self, a: str):
            self.a = a

    class B:
        pass

    def create_a(foo: str, bar: B)->A:
        return A(foo)


    class MyContainer(StaticContainer):
        def configure(self, config: Config):
            # use config's instance method to specify that a particular instance shall be used
            config.callable(create_a, foo="bar")
            # every time an object of type A is needed, the instance my_a will be returned

    container = create_container(MyContainer)
    a = container.get(A)
    print(a.a)

.. testoutput::

    bar

