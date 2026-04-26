"""Pytest hook implementation."""

from __future__ import annotations

import types
from typing import TYPE_CHECKING

import pytest
from beartype import beartype

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType


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
            # Bound methods proxy ``__annotate__`` to their underlying
            # function but do not allow assignment, so write through to
            # ``__func__`` for class-based tests.
            annotate_target = (
                underlying.__func__
                if isinstance(underlying, types.MethodType)
                else underlying
            )
            # Snapshot ``__annotate__`` before applying beartype: beartype
            # replaces it with a closure that crashes under
            # ``annotationlib.Format.STRING`` (beartype/beartype#637),
            # which breaks anything that later introspects the original
            # function's annotations in string form -- notably nested
            # ``pytest.main()`` re-collection of parametrized tests.
            saved_annotate = getattr(annotate_target, "__annotate__", None)
            cache[key] = beartype(obj=underlying)
            # B010 ordinarily prefers ``x.attr = ...`` over
            # ``setattr(x, "attr", ...)``, but ``__annotate__`` is a
            # Python 3.14+ attribute (PEP 749) not modelled by mypy or
            # pyright stubs on older versions; ``setattr`` bypasses the
            # static attribute check uniformly.
            setattr(annotate_target, "__annotate__", saved_annotate)  # noqa: B010
        item.obj = cache[key]
