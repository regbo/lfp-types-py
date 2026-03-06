from collections.abc import Iterable as IterableABC
from typing import TypeVar

import pytest

import lfp_types
from lfp_types import (
    Container,
    is_container,
    is_iterable,
    is_sequence,
    to_bool,
    to_container,
    to_iterable,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ([1, 2], True),
        ((1, 2), True),
        ({1, 2}, True),
        ((x for x in range(2)), True),
        ("abc", False),
        (b"abc", False),
        (bytearray(b"abc"), False),
        (memoryview(b"abc"), False),
        (5, False),
        (None, False),
    ],
)
def test_is_iterable(value: object, expected: bool) -> None:
    assert is_iterable(value) is expected


def test_container_runtime_type() -> None:
    assert isinstance([1, 2], Container)
    assert isinstance((1, 2), Container)
    assert isinstance((x for x in range(2)), Container)
    assert not isinstance("abc", Container)
    assert not isinstance(b"abc", Container)


def test_is_container_distinguishes_generators() -> None:
    assert is_container([1, 2]) is True
    assert is_container((1, 2)) is True
    assert is_container((x for x in range(2))) is False
    assert is_container("abc") is False


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ([1, 2], True),
        ((1, 2), True),
        ("abc", False),
        (b"abc", False),
        ((x for x in range(2)), False),
        (5, False),
    ],
)
def test_is_sequence(value: object, expected: bool) -> None:
    assert is_sequence(value) is expected


def test_to_iterable_scalar_wraps() -> None:
    assert list(to_iterable(5)) == [5]


def test_to_iterable_container_passthrough_semantics() -> None:
    assert list(to_iterable([1, 2])) == [1, 2]
    assert list(to_iterable((1, 2))) == [1, 2]


def test_to_iterable_flatten_false_preserves_nesting() -> None:
    assert list(to_iterable([[1, 2], [3]], flatten=False)) == [[1, 2], [3]]


def test_to_iterable_flatten_true_recursively_flattens() -> None:
    value = [1, [2, (3, [4])], 5]
    assert list(to_iterable(value, flatten=True)) == [1, 2, 3, 4, 5]


def test_to_iterable_flatten_does_not_split_string_like() -> None:
    value = ["ab", b"cd", bytearray(b"ef"), memoryview(b"gh"), ["ij"]]
    flattened = list(to_iterable(value, flatten=True))
    assert flattened == ["ab", b"cd", bytearray(b"ef"), memoryview(b"gh"), "ij"]


def test_to_container_container_returns_as_is() -> None:
    lst = [1, 2, 3]
    tup = (1, 2, 3)
    assert to_container(lst) is lst
    assert to_container(tup) is tup


def test_to_container_non_container_iterable_materialized() -> None:
    gen = (x for x in range(3))
    assert to_container(gen) == [0, 1, 2]


def test_to_container_scalar_wrapped() -> None:
    assert to_container(5) == [5]


def test_to_container_flatten_true_flattens_nested() -> None:
    assert to_container([[1, 2], [3]], flatten=True) == [1, 2, 3]


def test_to_container_flatten_true_keeps_flat_container_identity() -> None:
    lst = [1, 2, 3]
    result = to_container(lst, flatten=True)
    assert result is lst


@pytest.mark.parametrize("value", [True, "true", "t", "yes", "y", "1", "on", 1, 1.0])
def test_to_bool_truthy_values(value: object) -> None:
    assert to_bool(value) is True


@pytest.mark.parametrize("value", [False, "false", "f", "no", "n", "0", "off", 0, 0.0])
def test_to_bool_falsy_values(value: object) -> None:
    assert to_bool(value) is False


def test_to_bool_unrecognized_uses_default() -> None:
    assert to_bool("maybe", default=True) is True
    assert to_bool("maybe", default=False) is False


def test_to_bool_raises_when_default_none() -> None:
    with pytest.raises(ValueError):
        to_bool("maybe", default=None)


def test_typevars_a_to_z_exist() -> None:
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        value = getattr(lfp_types, ch)
        assert isinstance(value, TypeVar)


def test_dunder_all_includes_public_and_excludes_private() -> None:
    assert "to_iterable" in lfp_types.__all__
    assert "to_container" in lfp_types.__all__
    assert "to_bool" in lfp_types.__all__
    assert "Container" in lfp_types.__all__
    assert "_TRUE_VALUES" not in lfp_types.__all__
    assert "_FALSE_VALUES" not in lfp_types.__all__

    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        assert ch in lfp_types.__all__


def test_to_iterable_returns_iterable_object() -> None:
    result = to_iterable(1)
    assert isinstance(result, IterableABC)
