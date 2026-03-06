# lfp-types

Lightweight runtime typing helpers for iterable detection, container normalization, flattening, and bool parsing.

## Features

- Runtime container type that excludes string-like values.
- `is_iterable`, `is_container`, and `is_sequence` helper checks.
- `to_iterable` and `to_container` normalization helpers.
- Optional recursive flattening for nested iterables.
- `to_bool` parser with common truthy and falsy values.
- Public `TypeVar` exports for `A` through `Z`.

## Install

```bash
pip install .
```
