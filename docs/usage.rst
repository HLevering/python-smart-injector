=====
Usage
=====

Smart injector provides a bunch of easy-to-use functions and methods, which let you configure your container as
you need it quickly.



Basic example:
==============

.. testcode::

    from smart_injector import create_container

    class A:
        pass

    class B:
        def __init__(self, a: A):
            self.a = a

    container = create_container()
    b = container.get(B)
    print(isinstance(b.a, A))

If you have only dependencies on concrete types, no further configuration will be needed and you can use the Di container
as it is.

.. testoutput::

    True

Smart-injector relies on type annotations to resolve dependencies. Therefore type annotated code is a must have, if you
want to use smart-injector efficiently. For many cases smart-injector can resolve dependencies automatically. However,
there are some limitations for the automatic depenendency resolving mechanism.

- dependencies on abstract types
- dependencies on builtin types
- explicitly provide arguments
- setting lifetime of a dependency
- set dependency to a specific instance


These cases need explicitly configuration. Basically, container configuration follows this pattern:

.. code-block::

    from smart_injector import Config, create_container

    def my_configuration(config: Config):
        pass

    container = create_container(configure=my_configuration)
    # container.get(some_type)


First you define a function which takes one parameter of type :py:class:`smart_injector.Config`. Then you provide this
function as a parameter to the factory function :py:func:`smart_injector.create_container`. In your function you can use
the methods provided by the `Config` object to configure your container. In the next sections we will cover how this is
done in detail.


Dependencies on abstract types
==============================

Abstract types (classes that inherit from :py:meth:`abc.ABC` and have at least one :py:meth:`abc.abstractmethod`) cannot be
instantiated directly. There for it is impossible for smart-injector to resolve these kind of dependencies. An explicit
binding of an abstract class to a concrete class must be configured. This is done by using :py:meth:`smart_injector.Config.bind`.

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

    # create your own configuration function. This function must take a parameter of type Config
    def configure(config: Config):
        # use config's bind method to bind A to ConcretA
        config.bind(A, ConcretA)
        # now if there is a dependency on A ,then an instance of ConcretA will be injected

    # create an instance of your new defined container
    container = create_container(configure)
    a = container.get(A)
    a.do()

With the above configuration, the container will inject an instance of type `ConcreteA`, whenever there is a dependency
on `A`.

.. testoutput::

    Hello


Binding is not restricted to abstract classes. You can bind type A to type B as long as type B is a subclass of type A.
Moreover, it is possible to chain bindings. Let's take the last example and add one more class.


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

    def configure(config: Config):
        config.bind(A, ConcretA)
        config.bind(ConcretA, ConcretB)
        # now everytime when there is a dependency on A then ConcretB will be injected

    # create an instance of your new defined container
    container = create_container(configure)
    a = container.get(A)
    a.do()

Instead of `A` an instance of `ConcreteA` should be used, but since there is a binding from `ConcreteA` to `ConcreteB`
effectively there will be inject an instance of `ConcreteB`.

.. testoutput::

    World


Additionally, you can bind types to functions. For this to work, the function must return either an instance of that
type or an instance of a subclass of that type.

.. testcode::

    from abc import ABC, abstractmethod

    class A(ABC):
        @abstractmethod
        def do(self):
            pass

    class ConcretA(A):
        def do(self):
            print("Hello")


    class ADependency:
        pass

    def concret_a_factory(dependency: ADependency)->ConcretA:
        return ConcretA()


    def configure(config: Config):
        config.bind(A, concret_a_factory)
        # now everytime when there is a dependency on A then the object returned by concret_a_factory will be injected

    # create an instance of your new defined container
    container = create_container(configure)
    a = container.get(A)
    a.do()


In the above example "concrete_a_factory" was called to get an instance of A. In addition, the dependencies of
conrete_a_factory are injected automatically.

.. testoutput::

    Hello


Dependencies on builtin types
=============================

Dependencies on builtin types are default constructed by default.

.. testcode::

    container = create_container()
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


This is rather useful. Therefore, a method for providing values for constructor or function parameters would be useful.


Explicitly provide arguments
============================

You can provide arguments explicitly by configuring your container to do so. Either by specifying values for the arguments
or by specifying a factory function for an argument, which will be called when resolving dependencies.

Values for arguments
####################

Values for arguments can be set with :py:meth:`smart_injector.Config.arguments`.

.. testcode::

    class MyClass:
        def __init__(self, a: str, b: int, c: float):
            self.a = a
            self.b = b
            self.c = c

    def configure(config: Config):
        # use config's arguments method to provide some arguments
        config.arguments(MyClass, a="hello", b=42, c=1.0)
        # now everytime when there is a dependency on MyClass then MyClass(a="hello", b=42, c=1.0) will be inserted

    container = create_container(configure)
    a = container.get(MyClass)
    print(a.a)
    print(a.b)
    print(a.c)

In the above example `MyClass` will be created as `MyClass(a="hello", b=42, c=1.0)`.

.. testoutput::

    hello
    42
    1.0


If arguments are provided explicitly, it is not necessary to provide all arguments. Arguments which are not specified,
are resolved automatically by the DI container .

.. testcode::

    class Foo:
        pass

    class MyClass:
        def __init__(self, a: str, foo: Foo, c: float):
            self.a = a
            self.foo = foo
            self.c = c

    def configure(config: Config):
        # use config's arguments method to provide some arguments
        config.arguments(MyClass, a="hello", c=1.0)

    container = create_container(configure)
    a = container.get(MyClass)
    print(a.a)
    print(isinstance(a.foo, Foo))
    print(a.c)

In the above example no argument for parameter `foo` was specified. Therefore, the dependency on `foo` is resolved by the
container. In this case it is a default constructed `Foo()`.

.. testoutput::

    hello
    True
    1.0


By explicitly providing arguments it is also possible to resolve dependencies without type annotations.

 .. testcode::

    class MyClass:
        def __init__(self, a):
            self.a = a

    def configure(config: Config):
        # use config's arguments method to provide some arguments
        config.arguments(MyClass, a="hello")
        # now everytime when there is a dependency on MyClass then MyClass(a="hello", b=42, c=1.0) will be inserted

    container = create_container(configure)
    a = container.get(MyClass)
    print(a.a)

There is no type annotation for `MyClass` parameter `a`. Anyhow, the value "hello" is injected correctly for parameter
`a`.

.. testoutput::

    hello

.. note:: At the moment only keyword arguments can be provided with arguments. Moreover, you cannot provide the keyword
          argument "where" which is used to specify arguments in a specific context (see Context section for further
          information).


Setting factories for arguments
###############################

Instead of providing values for parameters, it is also possible to define a function which will be called to retrieve the
value for the parameter. A factory for a parameter is set with :py:meth:`smart_injector.Config.arg_factory`.

.. testcode::

    class MyClass:
        def __init__(self, a: str):
            self.a = a

    def get_a()->str:
        return "hello"

    def configure(config: Config):
        config.arg_factory(MyClass, a=get_a)

    container = create_container(configure)
    a = container.get(MyClass)
    print(a.a)

Result:

.. testoutput::

    hello

You can provide any callable as a factory. If necessessary, dependencies of the factory function are injected automatically
by smart_injector. Additionally, if you provide a method of a factory function, smart_injector will create a class instance
and then call that method. (smart_injector will also create and inject all dependencies to create that instance automatically)

.. testcode::

    class MyInt:
        def get_int(self) -> int:
            return 42


    class ProvidesInt:
        def __init__(self, a_int: MyInt):
            self._a_int = a_int

        def get_int(self) -> int:
            return self._a_int.get_int()


    class NeedsInt:
        def __init__(self, a_int: int):
            self.a_int = a_int


    def configure(config: Config):
        config.arg_factory(NeedsInt, a_int=ProvidesInt.get_int)

    container = create_container(configure)
    needs_int = container.get(NeedsInt)
    print(needs_int.a_int)

Smart_injector creates an instance of ProvidesInt automatically (and it will inject an instance of MyInt into it). Then it
calls method "get_int" of that previously created instance.

.. testoutput::

    42

For this kind of factory methods it is impossible to set arguments for the method explicitly with :py:meth:`smart_injector.Config.arguments`.

Setting dependency's lifetime
=============================

By default all injected objects have a transient lifetime. That means, that every time when an object is needed a new
instance of that object is created.


.. testcode::

    class A:
        pass

    class B:
        pass

    from smart_injector import Lifetime

    def configure(config: Config):
        # use config's lifetime method to specify an objects lifetime
        config.lifetime(A, lifetime=Lifetime.SINGLETON)
        # now there will be only one object of type A, which will be inserted wherever an object A is needed
        config.lifetime(B, lifetime=Lifetime.TRANSIENT)
        # everytime a new object B is created. This is the default behaviour for all types

    container = create_container(configure)
    a1 = container.get(A)
    a2 = container.get(A)
    b1 = container.get(B)
    b2 = container.get(B)
    print(a1 is a2)
    print(b1 is b2)

`b1` and `b2` refer to the same object since lifetime of `B` was defined as `SINGLETON`.

.. testoutput::

    True
    False


It is possible to override the default lifetime for objects created by a container. This must be done when the container
is created.

.. testcode::

    class A:
        pass


    from smart_injector import Lifetime

    container = create_container(default_lifetime=Lifetime.SINGLETON)
    a1 = container.get(A)
    a2 = container.get(A)
    print(a1 is a2)

.. testoutput::

    True


Specify a specific instance
===========================

If you want a specific instance to be used for a type, you can do that, too. You have specify the instance with
:py:meth:`smart_injector.Config.instance`.


.. testcode::

    class A:
        def __init__(self, a: str):
            self.a = a

    my_a = A("foo")

    def configure(config: Config):
        # use config's instance method to specify that a particular instance shall be used
        config.instance(A, my_a)
        # every time an object of type A is needed, the instance my_a will be returned

    container = create_container(configure)
    a1 = container.get(A)
    print(a1 is my_a)

.. testoutput::

    True

# TODO explanation for contexts and `where` parameter


Get a configured object from the container
==========================================

When you ask the container to provide you an object of type `T` by calling :py:meth:`smart_injector.StaticContainer.get`
with `T`, the container will provide and configure the object in a specific way.

Resolving Order
###############

First of all, the container determines, which real type is requested and if a new instance has to be created:


#. If an instance of T was set with :py:meth:`smart_injector.Config.instance` method, use this instance of T.
#. If a binding was specified for T with :py:meth:`smart_injector.Config.bind`, use the bounded type instead of T and start again
   with a new request with the bounded type.
#. If T's lifetime is singleton(with :py:meth:`smart_injector.Config.lifetime` or :py:meth:`smart_injector.create_container`
   and default_lifetime = :py:attr:`smart_injector.Lifetime.SINGLETON`, create a new
   instance of T at the first request. Return the same instance on every subsequent request.
#. If T is a builtin type, than use the type's default constructor.
#. Create a new instance of T.


New Instance Creation
#####################

When a new instance of T must be created. The container will resolve all dependencies of T via the following schema:

#. Determine all dependencies of T. This means all argument of T's constructor, if is a class or of T itself if it is a
   function.
#. Remove all dependencies of T, which were already set with :py:meth:`smart_injector.Config.arguments` or
   :py:meth:`smart_injector.Config.arg_factory`.
#. Resolve the remaining dependencies by asking the container to resolve each dependency.
#. For every argument, for which there was set a factory with `Config.arg_factory`, call that factory function.
   This is done by asking the container to resolve the factory function by calling :py:meth:`smart_injector.StaticContainer.get`.
   Therefore, all dependencies of that factory function are resolved automatically, too.
#. Create the new oject of type T with the former resolved dependencies injected.



