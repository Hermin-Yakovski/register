# Register Key Constraints Design (Revised)

**Date:** 2026-06-29
**Status:** Draft
**Author:** Design Session
**Revises:** [2026-06-25-register-key-constraints-design.md](2026-06-25-register-key-constraints-design.md)

## Overview

Constrain the TypeVar `K` in `Register(Generic[K])` so that any key type must provide:
1. Identity fields: `id: int`, `name: str`, `name_cn: str`
2. Aggregation methods: `sum`, `mean`, `min`, `max`, `range`
3. Validation: `validate(data, **config) -> bool`

This is enforced via an ABC (`RegisterKey`) that key types must inherit from. Three concrete key classes are provided: `ParameterKey` (scalar values), `PositionKey` (tuples of fixed arity), and `IterableKey` (variable-length iterables). The `Method` enum gains a `MEAN` entry.

## Architecture

### Class Hierarchy

```
RegisterKey (ABC, public) — the protocol
└── _BaseKey (private) — shared implementation
    ├── ParameterKey   # scalar values
    ├── PositionKey    # + arity, element-wise aggregation
    └── IterableKey    # per-iterable reduction
```

### File Layout

```
register/
├── key.py          # RegisterKey, _BaseKey, ParameterKey, PositionKey, IterableKey
├── register.py     # K = TypeVar("K", bound=RegisterKey), Method + MEAN, Register + validate
├── parameter.py    # Id, Code, Name as ParameterKey singletons
├── dimension.py    # Unchanged
├── exception.py    # Unchanged
└── __init__.py     # Updated exports
```

### Exports

```python
from .key import RegisterKey, ParameterKey, PositionKey, IterableKey
from .register import Register
from .parameter import Id, Code, Name
from .dimension import Dimension, Index, Metric
from .exception import RegisterError, ValidationError, DimensionError

__all__ = [
    "Register",
    "RegisterKey",
    "ParameterKey",
    "PositionKey",
    "IterableKey",
    "Dimension",
    "Index",
    "Metric",
    "Id",
    "Code",
    "Name",
    "RegisterError",
    "ValidationError",
    "DimensionError",
]
```

- `_BaseKey` is **not** exported — it is a private implementation detail.
- `Dimension` is unchanged and is **not** a `RegisterKey`.

## RegisterKey ABC

New file `register/key.py`:

```python
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .register import DimensionAsKey


class RegisterKey(ABC):
    """Public protocol for any class used as a key in Register[K].

    Provides identity (id, name, name_cn), five aggregation methods,
    and a validate method for checking stored data.
    """

    @property
    @abstractmethod
    def id(self) -> int: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def name_cn(self) -> str: ...

    @abstractmethod
    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool: ...
```

**Design decisions:**
- Properties are read-only (no setters) — key identity is immutable after creation.
- All methods take `data: DimensionAsKey` as the first argument — the data source to operate on.
- `*args: Any, **kwargs: Any` are placeholders; exact semantics for filtering/selection are TBD.
- `RegisterKey` defines the contract only; common implementation lives in `_BaseKey`.

## _BaseKey

Private base class providing shared identity fields and dunder methods:

```python
class _BaseKey(RegisterKey):
    """Internal base — not exported. Provides identity fields and common behavior."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: Any = None) -> None:
        self._id = id
        self._name = name
        self._name_cn = name_cn
        self.vtype = vtype

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self._id == getattr(other, "_id", None)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn
```

**Design decisions:**
- `__eq__` uses `self.__class__` — a `ParameterKey(1, ...)` is **not** equal to a `PositionKey(1, ...)`. Each subclass has its own identity space.
- `vtype` lives on `_BaseKey` since all three concrete classes use it. `PositionKey` adds `arity` on top.
- Properties are read-only — key identity is immutable.

## ParameterKey

Scalar values. Aggregation operates on individual values.

```python
class ParameterKey(_BaseKey):
    """Key for scalar values."""

    # Inherits id, name, name_cn, vtype, __hash__, __eq__, __str__, __repr__ from _BaseKey
    # Implements sum, mean, min, max, range, validate
```

### Aggregation Behavior (vtype dispatch)

#### `sum(self, data, *args, **kwargs) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool` | `sum(args)` | Returns `0` |
| `str` or `Dimension` instance | `dict(Counter(args))` — frequency count | Returns `{}` |
| Other | `NotImplementedError` | N/A |

**Note:** `sum` is the only method that does NOT guard against empty args — `sum(())` naturally returns `0`.

#### `mean(self, data, *args, **kwargs) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool` | `sum(args) / len(args)` | `RegisterError` |
| Other | `NotImplementedError` | N/A |

#### `min(self, data, *args, **kwargs) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool`, `str` | `min(args)` | `RegisterError` |
| Other (including `Dimension`) | `NotImplementedError` | N/A |

#### `max(self, data, *args, **kwargs) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool`, `str` | `max(args)` | `RegisterError` |
| Other (including `Dimension`) | `NotImplementedError` | N/A |

#### `range(self, data, *args, **kwargs) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool` | `max(args) - min(args)` | `RegisterError` |
| Other (including `str`, `Dimension`) | `NotImplementedError` | N/A |

### validate

```python
def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
    # For every stored value in data: isinstance(value, self.vtype)
    # Returns False if any mismatch; True if all valid or vtype is None
```

## PositionKey

Tuples of fixed arity. Aggregation is **element-wise** across tuples using `zip(*args, strict=True)`.

```python
class PositionKey(_BaseKey):
    """Key for positional values — tuples of the same length."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: Any = None, arity: int = 0) -> None:
        super().__init__(id, name, name_cn, vtype)
        if arity < 1:
            raise RegisterError("arity must be >= 1")
        self.arity = arity
```

### Aggregation Behavior

- **Numeric vtype only** (`int`/`float`/`bool`). `str` and `Dimension` raise `NotImplementedError`.
- All methods operate element-wise: `[op(elems) for elems in zip(*args, strict=True)]`
- Result is always a `list` of length equal to `arity`.
- `zip(*args, strict=True)` raises `ValueError` if input tuples have mismatched lengths.

| Method | Behavior | Empty args |
|--------|----------|------------|
| `sum` | `[sum(elems) for elems in zip(*args, strict=True)]` | `RegisterError` |
| `mean` | `[sum(elems)/len(args) for elems in zip(*args, strict=True)]` | `RegisterError` |
| `min` | `[min(elems) for elems in zip(*args, strict=True)]` | `RegisterError` |
| `max` | `[max(elems) for elems in zip(*args, strict=True)]` | `RegisterError` |
| `range` | `[max(elems)-min(elems) for elems in zip(*args, strict=True)]` | `RegisterError` |

### validate

```python
def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
    # For every stored value in data:
    #   isinstance(value, tuple) and len(value) == self.arity
    #   and all isinstance(elem, self.vtype) for elem in value
    # Returns False if any mismatch
```

## IterableKey

Variable-length iterables of vtype. Aggregation is **per-iterable reduction** — each input iterable is summarized independently.

```python
class IterableKey(_BaseKey):
    """Key for iterable values — variable-length collections of vtype."""

    # Inherits id, name, name_cn, vtype from _BaseKey
    # Implements sum, mean, min, max, range, validate
```

### Aggregation Behavior

Each method reduces each input iterable independently, returning a list of per-iterable results. Result length = number of input iterables. Result is always a `list` regardless of input iterable type.

| Method | numeric | str | Dimension | Empty iterable |
|--------|---------|-----|-----------|----------------|
| `sum` | `sum(iterable)` per arg | `dict(Counter(iterable))` per arg | `dict(Counter(iterable))` per arg | `0` / `{}` |
| `mean` | `sum(iterable)/len(iterable)` per arg | `NotImplementedError` | `NotImplementedError` | `RegisterError` |
| `min` | `min(iterable)` per arg | lex `min(iterable)` per arg | `NotImplementedError` | `RegisterError` |
| `max` | `max(iterable)` per arg | lex `max(iterable)` per arg | `NotImplementedError` | `RegisterError` |
| `range` | `max(iterable)-min(iterable)` per arg | `NotImplementedError` | `NotImplementedError` | `RegisterError` |

**Example:**

```python
itr = IterableKey(1, "scores", "分数", vtype=int)
itr.sum(data, [1, 2, 3], [4, 5])  # => [6, 9]
itr.mean(data, [1, 2, 3], [4, 5])  # => [2.0, 4.5]
itr.min(data, [1, 2, 3], [4, 5])  # => [1, 4]
itr.max(data, [1, 2, 3], [4, 5])  # => [3, 5]
itr.range(data, [1, 2, 3], [4, 5])  # => [2, 1]
```

### validate

```python
def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
    # For every stored value in data:
    #   it is iterable and all isinstance(elem, self.vtype) for elem in value
    # Returns False if any mismatch
```

## Method Enum

```python
class Method(int):
    _NAMES: dict[int, str] = {0: "ALL", 1: "SUM", 2: "MAX", 3: "MIN", 4: "RANGE", 5: "MEAN"}
```

## Register Class

```python
from .key import RegisterKey

K = TypeVar("K", bound=RegisterKey)


class Register(Generic[K]):
    ALL: Method = Method(0)
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    MEAN: Method = Method(5)
    # ... rest unchanged

    def validate(self, **config: Any) -> bool:
        rs = True
        for key in self._data:
            data = self._data[key]
            rs &= key.validate(data, **config)
        return rs
```

**Changes from current codebase:**
- `K` is now bounded: `TypeVar("K", bound=RegisterKey)`
- `MEAN = Method(5)` added
- `validate()` method added, delegating to each key's `validate(data, **config)`

## parameter.py

Slimmed down to predefined `ParameterKey` singletons:

```python
from .key import ParameterKey

Id = ParameterKey(1, "id", "ID", int)
Code = ParameterKey(2, "code", "编码", str)
Name = ParameterKey(3, "name", "名称", str)

__all__ = ["Id", "Code", "Name"]
```

## Dimension (Unchanged)

`Dimension` is not modified in this change. It currently lacks an `id` field and cannot be used as a `RegisterKey`. An `id` field can be added in a future change to make `Dimension` eligible as a Register key.

## Summary of Changes vs. Original Spec

| Topic | Original (06-25) | Revised (06-29) |
|---|---|---|
| Class names | `Parameter`, `IterParameter` | `ParameterKey`, `PositionKey`, `IterableKey` |
| Hierarchy | Flat siblings from `RegisterKey` | `RegisterKey` → `_BaseKey` → 3 concrete classes |
| `BaseKey` | Not present | `_BaseKey` (private) — shared identity + dunder methods |
| `PositionKey` | Didn't exist (was "IterParameter") | New: fixed `arity`, element-wise, numeric only |
| `IterableKey` | Didn't exist | New: per-iterable reduction, all vtypes |
| `validate` | Not in spec | Abstract on `RegisterKey`, implemented by each subclass |
| Method signatures | `(self, *args, **kwargs)` | `(self, data: DimensionAsKey, *args, **kwargs)` — `*args`/`**kwargs` semantics TBD |
| `__eq__` | `isinstance(other, Parameter)` | `isinstance(other, self.__class__)` — cross-class inequality |
| `MEAN` | Added | Still added |