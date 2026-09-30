pytest-beartype-tests
=====================

.. warning::

   This plugin has been superseded by `pytest-beartype <https://pypi.org/project/pytest-beartype/>`_ 0.3.0.
   Enable ``beartype_tests = true`` in your pytest configuration or pass ``--beartype-tests`` to check test functions with it.
   The new plugin can also check fixtures and application packages; see its `README <https://github.com/beartype/pytest-beartype#usage>`_ for configuration.
   Version 0.3.0 currently requires a Beartype 0.23.0 release candidate. Version 0.23.0rc2 is available on PyPI.

A tiny pytest plugin that applies `beartype <https://github.com/beartype/beartype>`_ to every collected test function, giving you runtime type-checking of test signatures and any locally-typed variables inside the test body.

Install
-------

.. code-block:: sh

   uv add --dev pytest-beartype-tests

The plugin auto-registers via the ``pytest11`` entry point, so there is no configuration.

What it does
------------

Equivalent to writing this hook in your ``conftest.py``:

.. code-block:: python

   import pytest
   from beartype import beartype


   def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
       for item in items:
           item.obj = beartype(obj=item.obj)
