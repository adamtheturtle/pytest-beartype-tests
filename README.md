# pytest-beartype-tests

A tiny pytest plugin that applies [`beartype`](https://github.com/beartype/beartype) to every collected test function, giving you runtime type-checking of test signatures and any locally-typed variables inside the test body.

This is distinct from [`pytest-beartype`](https://pypi.org/project/pytest-beartype/), which beartypes your *source* packages. This plugin beartypes the *tests themselves*.

## Install

```sh
uv add --dev pytest-beartype-tests
```

The plugin auto-registers via the `pytest11` entry point — there is no configuration.

## What it does

Equivalent to writing this hook in your `conftest.py`:

```python
import pytest
from beartype import beartype


def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    for item in items:
        item.obj = beartype(obj=item.obj)
```

## License

MIT
