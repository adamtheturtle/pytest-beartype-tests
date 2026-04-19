"""Behavioural tests for the pytest-beartype-tests plugin."""

import pytest

_COUNTING_CONFTEST = """
from beartype import beartype as _real_beartype
import pytest

from pytest_beartype_tests import plugin as _plugin

_calls = {"n": 0}

def _counting_beartype(*, obj):
    _calls["n"] += 1
    return _real_beartype(obj=obj)

_plugin.beartype = _counting_beartype


@pytest.fixture
def beartype_call_count() -> dict:
    return _calls
"""


def test_type_correct_test_passes(pytester: pytest.Pytester) -> None:
    """A test whose values match their annotations runs normally."""
    _ = pytester.makepyfile(  # pyright: ignore[reportUnknownMemberType]
        """
        def test_ok() -> None:
            x: int = 1
            assert x == 1
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_argument_violating_annotation_fails(
    pytester: pytest.Pytester,
) -> None:
    """Parametrized values that violate a type annotation fail."""
    _ = pytester.makepyfile(  # pyright: ignore[reportUnknownMemberType]
        """
        import pytest

        @pytest.mark.parametrize("value", [1, "not-an-int"])
        def test_param(value: int) -> None:
            pass
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, failed=1)


def test_class_based_test_is_type_checked(
    pytester: pytest.Pytester,
) -> None:
    """Methods on test classes are also wrapped with beartype."""
    _ = pytester.makepyfile(  # pyright: ignore[reportUnknownMemberType]
        """
        import pytest

        class TestThing:
            @pytest.mark.parametrize("value", ["bad"])
            def test_method(self, value: int) -> None:
                pass
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)


def test_wrapper_cached_across_parametrized_items(
    pytester: pytest.Pytester,
) -> None:
    """Parametrized items share a single beartype wrapper."""
    _ = pytester.makeconftest(_COUNTING_CONFTEST)
    _ = pytester.makepyfile(  # pyright: ignore[reportUnknownMemberType]
        """
        import pytest

        @pytest.mark.parametrize("value", [1, 2, 3, 4])
        def test_param(value: int, beartype_call_count: dict) -> None:
            assert beartype_call_count["n"] == 1
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=4)


def test_each_distinct_function_is_wrapped_once(
    pytester: pytest.Pytester,
) -> None:
    """Distinct test functions each get their own beartype call."""
    _ = pytester.makeconftest(_COUNTING_CONFTEST)
    _ = pytester.makepyfile(  # pyright: ignore[reportUnknownMemberType]
        """
        def test_one(beartype_call_count: dict) -> None:
            assert beartype_call_count["n"] == 2

        def test_two(beartype_call_count: dict) -> None:
            assert beartype_call_count["n"] == 2
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_same_named_methods_in_different_classes_keep_own_types(
    pytester: pytest.Pytester,
) -> None:
    """Same-named methods in different classes get class-specific wrappers."""
    _ = pytester.makepyfile(  # pyright: ignore[reportUnknownMemberType]
        """
        import pytest

        class TestInt:
            @pytest.mark.parametrize("value", [1])
            def test_same_name(self, value: int) -> None:
                pass

        class TestStr:
            @pytest.mark.parametrize("value", [1])
            def test_same_name(self, value: str) -> None:
                pass
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, failed=1)


def test_return_annotation_is_enforced(pytester: pytest.Pytester) -> None:
    """A test returning a value that violates its return annotation fails."""
    _ = pytester.makepyfile(  # pyright: ignore[reportUnknownMemberType]
        """
        def test_bad_return() -> None:
            return "not None"  # type: ignore[return-value]
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)
