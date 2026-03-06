# lfp-types

Lightweight runtime typing helpers for iterable detection, container normalization, flattening, and bool parsing.

## Features

- **Runtime Container Type**: `Container[T]` that excludes string-like values (str, bytes, etc).
- **Type Guards**: `is_iterable`, `is_container`, and `is_sequence` helper checks.
- **Normalization**: `to_iterable` and `to_container` helpers to handle scalars and collections uniformly.
- **Flattening**: Optional recursive flattening for nested iterables.
- **Boolean Parsing**: `to_bool` parser with support for common truthy and falsy string/numeric values.
- **Type Variables**: Public `TypeVar` exports for `A` through `Z`.

## Install

```bash
pip install lfp-types
```

## Usage

### Iterable and Container Checks

Check if a value is a non-string iterable or container.

```python
from lfp_types import is_iterable, is_container, Container

is_iterable([1, 2, 3])  # True
is_iterable("abc")      # False (strings are excluded by design)
is_iterable(b"abc")     # False

is_container([1, 2, 3])     # True
is_container(iter([1, 2]))  # False (iterators/generators are not containers)

isinstance([1, 2, 3], Container)  # True
```

### Normalization and Flattening

Ensure you are working with an iterable or a materialized container.

```python
from lfp_types import to_iterable, to_container

# Normalize scalars to iterables
list(to_iterable(5))  # [5]

# Pass through existing iterables
list(to_iterable([1, 2]))  # [1, 2]

# Recursive flattening
list(to_iterable([1, [2, [3]]], flatten=True))  # [1, 2, 3]

# Normalize to a list/materialized container
to_container(iter([1, 2]))  # [1, 2]
```

### Boolean Parsing

Convert various representations to a boolean.

```python
from lfp_types import to_bool

to_bool("yes")   # True
to_bool("off")   # False
to_bool("1")     # True
to_bool(0)       # False

# Custom default for unrecognized values
to_bool("maybe", default=True)  # True

# Raise ValueError if default is None
to_bool("invalid", default=None)  # Raises ValueError
```

### Type Variables

Quick access to standard `TypeVar` names.

```python
from lfp_types import A, B, T

def map_items(items: list[A]) -> list[B]:
    ...
```

## Development

This project uses [pixi](https://pixi.sh) for environment management and [uv](https://github.com/astral-sh/uv) for builds.

```bash
pixi run pytest
```
