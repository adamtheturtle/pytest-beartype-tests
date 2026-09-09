"""Pytest hook implementation."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

import pytest
from beartype import beartype

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType


def _beartyped_proxy(
    *, function: Callable[..., object]
) -> Callable[..., object]:
    """Decorate a proxy without mutating ``function`` metadata."""

    @wraps(wrapped=function)
    def proxy(*args: object, **kwargs: object) -> object:
        """Call the original test function."""
        return function(*args, **kwargs)

    return beartype(obj=proxy)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply the beartype decorator to all collected test functions."""
    # Parametrized tests share one underlying function across many items;
    # cache the wrapper so beartype only compiles it once per function.
    cache: dict[
        tuple[ModuleType | None, type | None, str], Callable[..., object]
    ] = {}
    for item in items:
        if not isinstance(item, pytest.Function):
            # e.g. Sybil doc-test items are not ``pytest.Function`` instances.
            continue
        key = (item.module, item.cls, item.originalname)
        if key not in cache:
            underlying = item.obj
            # Beartype mutates the function metadata it decorates. Decorate a
            # metadata-preserving proxy so the collected function keeps its
            # original deferred annotations for later introspection and
            # nested re-collection.
            cache[key] = _beartyped_proxy(
                function=underlying,
            )
        item.obj = cache[key]
