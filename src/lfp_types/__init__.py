import string
from collections.abc import Iterable, Iterator, Sequence
from types import GeneratorType
from typing import Any, Generic, TypeVar

"""Runtime helpers and normalization utilities for iterable-like values."""

T = TypeVar("T")
_STRING_LIKE = (str, bytes, bytearray, memoryview)


class _ContainerMeta(type):
    def __instancecheck__(cls, instance: Any) -> bool:
        return isinstance(instance, Iterable) and not isinstance(instance, _STRING_LIKE)


class Container(Generic[T], metaclass=_ContainerMeta):
    """Runtime-checkable iterable container excluding string-like objects."""


def is_iterable(value: Any) -> bool:
    return isinstance(value, Iterable) and not isinstance(value, _STRING_LIKE)


def is_container(value: Any) -> bool:
    return is_iterable(value) and not isinstance(value, GeneratorType)


def is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, _STRING_LIKE)


def to_iterable(value: Any, *, flatten: bool = False) -> Iterable[Any]:
    """
    Normalize a value to an iterable.

    Scalars become a single-element iterable.
    Iterable containers pass through unchanged when flatten=False.

    flatten=True recursively flattens nested iterables.
    """
    if not flatten and is_iterable(value):
        return value

    def _to_iterable(cur_value: Any) -> Iterator[Any]:
        if not is_iterable(cur_value):
            yield cur_value
        elif not flatten:
            yield from cur_value
        else:
            for v in cur_value:
                yield from _to_iterable(v)

    return _to_iterable(value)


def to_container(value: Any, *, flatten: bool = False) -> Iterable[Any]:
    """
    Normalize a value to a container.

    Container values pass through unchanged unless flatten=True.
    Non-container iterables are materialized.
    Scalars become a single-element list.
    """
    if is_container(value) and (not flatten or not any(is_iterable(v) for v in value)):
        return value
    return list(to_iterable(value, flatten=flatten))


_TRUE_VALUES = {"true", "t", "yes", "y", "1", "on"}
_FALSE_VALUES = {"false", "f", "no", "n", "0", "off"}


def to_bool(value: Any, *, default: bool | None = False) -> bool:
    """
    Convert common truthy / falsy representations to bool.

    Numeric handling
        1 / 1.0 -> True
        0 / 0.0 -> False
    """

    if isinstance(value, bool):
        return value

    elif isinstance(value, (int, float)):
        if value == 1:
            return True
        elif value == 0:
            return False

    elif value is not None and (value_str := str(value).strip().lower()):
        if value_str in _TRUE_VALUES:
            return True
        elif value_str in _FALSE_VALUES:
            return False

    if default is None:
        raise ValueError(f"Cannot convert {value!r} to bool")

    return default


# ---------------------------------------------------------------------
# Generate TypeVars A-Z (T is already defined)
# ---------------------------------------------------------------------

for _name in string.ascii_uppercase:
    if _name != "T":
        globals()[_name] = TypeVar(_name)


# ---------------------------------------------------------------------
# Export everything public
# ---------------------------------------------------------------------

__all__ = [
    name
    for name, value in globals().items()
    if not name.startswith("_") and getattr(value, "__module__", "") == __name__
]
