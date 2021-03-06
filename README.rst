========
Overview
========
Smart-injector is an lightweight dependency injection framework for Python.
It was designed to be an easy to use tool to implement dependency injection in your application in a pythonic way.

Key features are:
- Ligtweight
- pure python
- leverages type annotations
- scopes
- non invasive


Project Status
==============

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-smart-injector/badge/?style=flat
    :target: https://readthedocs.org/projects/python-smart-injector
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/hlevering/python-smart-injector.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/hlevering/python-smart-injector

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/hlevering/python-smart-injector?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/hlevering/python-smart-injector

.. |requires| image:: https://requires.io/github/HLevering/python-smart-injector/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/HLevering/python-smart-injector/requirements/?branch=master
.. |codecov| image:: https://codecov.io/gh/HLevering/python-smart-injector/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/gh/HLevering/python-smart-injector

.. |version| image:: https://img.shields.io/pypi/v/smart-injector.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/smart-injector

.. |wheel| image:: https://img.shields.io/pypi/wheel/smart-injector.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/smart-injector

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/smart-injector.svg
    :alt: Supported versions
    :target: https://pypi.org/project/smart-injector

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/smart-injector.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/smart-injector

.. |commits-since| image:: https://img.shields.io/github/commits-since/hlevering/python-smart-injector/v0.0.6.svg
    :alt: Commits since latest release
    :target: https://github.com/hlevering/python-smart-injector/compare/v0.0.6...master



.. end-badges


Installation
============

::

    pip install smart-injector

You can also install the in-development version with::

    pip install https://github.com/hlevering/python-smart-injector/archive/master.zip


Quickstart
==========

Basic Usage::

    >>> class A:
    ...     pass
    ...
    >>> class B:
    ...     def __init__(self, a: A):
    ...         self.a = a
    ...
    >>> container = create_container(StaticContainer)
    >>> b = container.get(B)
    >>> isinstance(b.a, A)
    True



Documentation
=============

Detailed documentation can be found here:

https://python-smart-injector.readthedocs.io/

Further usage examples can be found here:
https://python-smart-injector.readthedocs.io/en/latest/usage.html


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
