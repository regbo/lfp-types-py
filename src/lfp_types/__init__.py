"""Lightweight runtime typing helpers for iterable detection, container
normalization, flattening, and bool parsing.

This module intentionally treats string-like values (``str``, ``bytes``,
``bytearray``, ``memoryview``) as scalars, not as iterable containers. Most
real-world code wants ``is_iterable("abc")`` to return ``False``, and this
module enforces that policy consistently across every helper.

Public surface:

- ``Container[T]``: runtime-checkable generic container type.
- ``is_iterable``, ``is_container``, ``is_sequence``: type-guard helpers.
- ``to_iterable``, ``to_container``: normalize scalars or iterables into a
  consistent iterable/container shape, with optional recursive flattening.
- ``to_bool``: parse common truthy/falsy numeric and string values.
- ``A`` through ``Z``: pre-declared ``TypeVar`` shortcuts.
"""

import string
from collections.abc import Iterable, Iterator, Sequence
from types import GeneratorType
from typing import Any, Generic, TypeVar

T = TypeVar("T")
_STRING_LIKE = (str, bytes, bytearray, memoryview)


class _ContainerMeta(type):
    """Metaclass that makes ``Container`` usable with ``isinstance``.

    ``isinstance(obj, Container)`` returns ``True`` for any iterable that is
    not a string-like value. This allows callers to write container checks
    without importing ``collections.abc.Iterable`` or repeating the
    string-exclusion rule at every call site.
    """

    def __instancecheck__(cls, instance: Any) -> bool:
        return isinstance(instance, Iterable) and not isinstance(instance, _STRING_LIKE)


class Container(Generic[T], metaclass=_ContainerMeta):
    """Runtime-checkable iterable container type that excludes string-like values.

    Use this where you want both a typing hint and an ``isinstance`` check
    that accepts lists, tuples, sets, generators, and custom iterables, but
    rejects ``str``, ``bytes``, ``bytearray``, and ``memoryview``.

    Examples:
        >>> isinstance([1, 2, 3], Container)
        True
        >>> isinstance("abc", Container)
        False
        >>> isinstance(b"abc", Container)
        False
        >>> isinstance((x for x in range(2)), Container)
        True

    Note:
        ``Container`` is not subscriptable at runtime for ``isinstance``; use
        the bare class. The generic parameter ``T`` is for static typing.
    """


def is_iterable(value: Any) -> bool:
    """Return ``True`` if ``value`` is iterable and not string-like.

    Args:
        value: Any object.

    Returns:
        ``True`` for lists, tuples, sets, dicts, generators, and other
        iterables. ``False`` for ``str``, ``bytes``, ``bytearray``,
        ``memoryview``, and non-iterable scalars.

    Examples:
        >>> is_iterable([1, 2])
        True
        >>> is_iterable("abc")
        False
        >>> is_iterable(5)
        False
    """
    return isinstance(value, Iterable) and not isinstance(value, _STRING_LIKE)


def is_container(value: Any) -> bool:
    """Return ``True`` if ``value`` is iterable, not string-like, and not a generator.

    A "container" here means something that can be iterated multiple times
    without being exhausted: lists, tuples, sets, dicts, custom collections,
    and any iterable that is not a one-shot generator.

    Args:
        value: Any object.

    Returns:
        ``True`` for lists, tuples, sets, dicts. ``False`` for generators,
        strings, bytes, and non-iterable scalars.

    Examples:
        >>> is_container([1, 2])
        True
        >>> is_container((x for x in range(2)))
        False
        >>> is_container("abc")
        False
    """
    return is_iterable(value) and not isinstance(value, GeneratorType)


def is_sequence(value: Any) -> bool:
    """Return ``True`` if ``value`` is a sequence and not string-like.

    A sequence supports indexed access and ``len()``. This includes lists
    and tuples but excludes sets, dicts, generators, and string-like values.

    Args:
        value: Any object.

    Returns:
        ``True`` for lists and tuples (and other ``Sequence`` subclasses).
        ``False`` for sets, dicts, generators, strings, and scalars.

    Examples:
        >>> is_sequence([1, 2])
        True
        >>> is_sequence((1, 2))
        True
        >>> is_sequence({1, 2})
        False
        >>> is_sequence("abc")
        False
    """
    return isinstance(value, Sequence) and not isinstance(value, _STRING_LIKE)


def to_iterable(value: Any, *, flatten: bool = False) -> Iterable[Any]:
    """Normalize ``value`` to an iterable.

    Scalars (including string-like values) are wrapped in a single-element
    iterable. Existing iterables pass through unchanged when ``flatten`` is
    ``False``. When ``flatten`` is ``True``, nested iterables are recursively
    expanded, but string-like elements are preserved intact (not split into
    characters or bytes).

    Args:
        value: Any object; scalar or iterable.
        flatten: If ``True``, recursively flatten nested iterables. Defaults
            to ``False``.

    Returns:
        An iterable view over ``value``. When ``flatten`` is ``False`` and
        ``value`` is already iterable, the same object is returned (no copy).
        Otherwise, a generator is returned.

    Examples:
        >>> list(to_iterable(5))
        [5]
        >>> list(to_iterable([1, 2]))
        [1, 2]
        >>> list(to_iterable([1, [2, [3]]], flatten=True))
        [1, 2, 3]
        >>> list(to_iterable("abc"))
        ['abc']
        >>> list(to_iterable([["ab"], b"cd"], flatten=True))
        ['ab', b'cd']
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
    """Normalize ``value`` to a re-iterable container.

    Unlike :func:`to_iterable`, this guarantees the result can be iterated
    more than once. One-shot iterables (generators) are materialized into a
    ``list``; existing containers pass through unchanged when possible.

    Args:
        value: Any object; scalar, iterable, or container.
        flatten: If ``True``, recursively flatten nested iterables. Defaults
            to ``False``. A flat input container short-circuits and is
            returned as-is even when ``flatten`` is ``True``.

    Returns:
        A container over ``value``. Either the original container (when
        safe) or a new ``list``. Never a generator.

    Examples:
        >>> to_container(5)
        [5]
        >>> to_container((x for x in range(3)))
        [0, 1, 2]
        >>> to_container([[1, 2], [3]], flatten=True)
        [1, 2, 3]
        >>> lst = [1, 2, 3]
        >>> to_container(lst) is lst
        True
    """
    if is_container(value) and (not flatten or not any(is_iterable(v) for v in value)):
        return value
    return list(to_iterable(value, flatten=flatten))


_TRUE_VALUES = {"true", "t", "yes", "y", "1", "on"}
_FALSE_VALUES = {"false", "f", "no", "n", "0", "off"}


def to_bool(value: Any, *, default: bool | None = False) -> bool:
    """Convert common truthy and falsy representations to ``bool``.

    Recognized values:

    - ``bool``: returned as-is.
    - ``int`` / ``float``: ``1`` or ``1.0`` is ``True``, ``0`` or ``0.0`` is
      ``False``. Other numerics fall through to ``default``.
    - ``str`` (case-insensitive, trimmed): ``"true"``, ``"t"``, ``"yes"``,
      ``"y"``, ``"1"``, ``"on"`` are ``True``; ``"false"``, ``"f"``,
      ``"no"``, ``"n"``, ``"0"``, ``"off"`` are ``False``.
    - Other types are first coerced via ``str(value)`` and checked against
      the same string sets.

    Args:
        value: The value to convert.
        default: Returned when ``value`` is not a recognized truthy or falsy
            representation. Pass ``None`` to raise ``ValueError`` instead.
            Defaults to ``False``.

    Returns:
        The parsed boolean, or ``default`` if no match is found.

    Raises:
        ValueError: If ``value`` is unrecognized and ``default`` is ``None``.

    Examples:
        >>> to_bool("yes")
        True
        >>> to_bool("OFF")
        False
        >>> to_bool(1)
        True
        >>> to_bool("maybe", default=True)
        True
        >>> to_bool("maybe", default=None)
        Traceback (most recent call last):
            ...
        ValueError: Cannot convert 'maybe' to bool
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
