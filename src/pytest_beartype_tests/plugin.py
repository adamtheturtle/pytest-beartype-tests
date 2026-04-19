"""Pytest hook implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from beartype import beartype

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

    import pytest


def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    """Apply the beartype decorator to all collected test functions."""
    # Parametrized tests share one underlying function across many items;
    # cache the wrapper so beartype only compiles it once per function.
    cache: dict[
        tuple[ModuleType | None, type | None, str], Callable[..., object]
    ] = {}
    for item in items:
        key = (item.module, item.cls, item.originalname)
        if key not in cache:
            cache[key] = beartype(obj=item.obj)
        item.obj = cache[key]
