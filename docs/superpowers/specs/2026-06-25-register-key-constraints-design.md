# Register Key Constraints Design

**Date:** 2026-06-25
**Status:** Approved
**Author:** Design Session

## Overview

Constrain the TypeVar `K` in `Register(Generic[K])` so that any key type must provide:
1. Identity fields: `id: int`, `name: str`, `name_cn: str`
2. Aggregation methods: `sum`, `mean`, `min`, `max`, `range`

This is enforced via an ABC (`RegisterKey`) that key types must inherit from. The `Method` enum gains a `MEAN` entry to stay in sync with the five aggregation methods.

## Architecture

### File Changes

```
register/
├── key.py          # NEW — RegisterKey ABC
├── register.py     # K = TypeVar("K", bound=RegisterKey), add MEAN to Method
├── parameter.py    # Parameter(RegisterKey) + new IterParameter(RegisterKey)
├── dimension.py    # Unchanged (id field can be added later)
├── exception.py    # Unchanged
└── __init__.py     # Export RegisterKey, IterParameter
```

### Key Relationships

- `RegisterKey` (ABC) defines the contract for any class used as a Register key
- `Parameter` inherits from `RegisterKey`, implements all abstract members
- `IterParameter` inherits from `RegisterKey`, adds `iter_vtype` and `flatten`/`strict` kwargs
- `Register[K]` binds K with `bound=RegisterKey` so type-checkers enforce the constraint
- `Method` enum gains `MEAN = Method(5)`

## RegisterKey ABC

New file `register/key.py`:

```python
from abc import ABC, abstractmethod
from typing import Any


class RegisterKey(ABC):
    """Abstract base class for Register key types.

    Any class used as a key in Register[K] must inherit from RegisterKey
    and implement the required properties and aggregation methods.
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
    def sum(self, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def mean(self, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def min(self, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def max(self, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def range(self, *args: Any, **kwargs: Any) -> Any: ...
```

**Design decisions:**
- Properties are read-only (no setters) — a key's identity shouldn't change after creation
- Aggregation methods are instance methods so different key instances can override behavior
- `*args: Any, **kwargs: Any` keeps signatures flexible for subclass-specific control parameters

## Parameter Changes

`Parameter` inherits from `RegisterKey`. The existing `_id`, `_name`, `_name_cn` properties satisfy the ABC requirements. Five aggregation methods are added with vtype-dependent behavior.

### Aggregation Method Behaviors

All methods follow the same structure: check `self.vtype` first, then apply logic.

#### `sum(self, *args: Any, **kwargs: Any) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool` | `sum(args)` | Returns `0` |
| `str` or `Dimension` instance | `dict(Counter(args))` — frequency count | Returns `{}` |
| Other | `NotImplementedError` | N/A |

**Note:** `sum` is the only method that does NOT guard against empty args — `sum(())` naturally returns `0`.

#### `mean(self, *args: Any, **kwargs: Any) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool` | `sum(args) / len(args)` | `RegisterError` |
| Other | `NotImplementedError` | N/A |

#### `min(self, *args: Any, **kwargs: Any) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool`, `str` | `min(args)` | `RegisterError` |
| Other (including `Dimension`) | `NotImplementedError` | N/A |

#### `max(self, *args: Any, **kwargs: Any) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool`, `str` | `max(args)` | `RegisterError` |
| Other (including `Dimension`) | `NotImplementedError` | N/A |

#### `range(self, *args: Any, **kwargs: Any) -> Any`

| vtype | Behavior | Empty args |
|-------|----------|------------|
| `int`, `float`, `bool` | `max(args) - min(args)` | `RegisterError` |
| Other (including `str`, `Dimension`) | `NotImplementedError` | N/A |

### Parameter Implementation

```python
from typing import Any
from .dimension import Dimension
from .exception import RegisterError
from .key import RegisterKey


class Parameter(RegisterKey):
    _id: int
    _name: str
    _name_cn: str
    vtype: Any

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
        return isinstance(other, Parameter) and self._id == other.id

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn

    def sum(self, *args: Any, **kwargs: Any) -> Any:
        if self.vtype in (int, float, bool):
            return sum(args)
        elif self.vtype is str or isinstance(self.vtype, Dimension):
            from collections import Counter
            return dict(Counter(args))
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("mean requires at least one value")
        if self.vtype in (int, float, bool):
            return sum(args) / len(args)
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        if self.vtype in (int, float, bool, str):
            return min(args)
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        if self.vtype in (int, float, bool, str):
            return max(args)
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        if self.vtype in (int, float, bool):
            return max(args) - min(args)
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")
```

## IterParameter

`IterParameter` is a sibling of `Parameter` (both inherit from `RegisterKey`). It represents a key whose values are iterables, with an additional `iter_vtype` field describing the container type (defaults to `list`).

### Control Parameters

Aggregation methods accept two kwargs:

| Kwarg | Default | Purpose |
|-------|---------|---------|
| `flatten` | `True` | When `True`, collapse all input iterables into one flat sequence and aggregate to a scalar. When `False`, aggregate element-wise across input iterables using `zip`. |
| `strict` | `False` | Passed to `zip(*args, strict=strict)`. When `True`, raises `ValueError` if input iterables have different lengths. |

### Str/Dimension vtype

For `sum` only: when `vtype` is `str` or a `Dimension` instance, `flatten` is ignored — the method always flattens all iterables and returns a frequency dict `dict[str, int]`.

### IterParameter Implementation

```python
class IterParameter(RegisterKey):
    _id: int
    _name: str
    _name_cn: str
    vtype: Any
    iter_vtype: Any

    def __init__(self, id: int, name: str, name_cn: str, vtype: Any = None, iter_vtype: Any = list) -> None:
        self._id = id
        self._name = name
        self._name_cn = name_cn
        self.vtype = vtype
        self.iter_vtype = iter_vtype

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, IterParameter) and self._id == other.id

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn

    def sum(self, *args: Any, **kwargs: Any) -> Any:
        flatten = kwargs.get("flatten", True)
        if self.vtype in (int, float, bool):
            if flatten:
                flat = [v for iterable in args for v in iterable]
                return sum(flat)
            return [sum(elements) for elements in zip(*args, strict=kwargs.get("strict", False))]
        elif self.vtype is str or isinstance(self.vtype, Dimension):
            from collections import Counter
            flat = [v for iterable in args for v in iterable]
            return dict(Counter(flat))
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, *args: Any, **kwargs: Any) -> Any:
        flatten = kwargs.get("flatten", True)
        strict = kwargs.get("strict", False)
        if self.vtype in (int, float, bool):
            if flatten:
                flat = [v for iterable in args for v in iterable]
                if not flat:
                    raise RegisterError("mean requires at least one value")
                return sum(flat) / len(flat)
            if not args:
                raise RegisterError("mean requires at least one value")
            return [sum(elements) / len(elements) for elements in zip(*args, strict=strict)]
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        flatten = kwargs.get("flatten", True)
        strict = kwargs.get("strict", False)
        if self.vtype in (int, float, bool, str):
            if flatten:
                flat = [v for iterable in args for v in iterable]
                if not flat:
                    raise RegisterError("min requires at least one value")
                return min(flat)
            return [min(elements) for elements in zip(*args, strict=strict)]
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        flatten = kwargs.get("flatten", True)
        strict = kwargs.get("strict", False)
        if self.vtype in (int, float, bool, str):
            if flatten:
                flat = [v for iterable in args for v in iterable]
                if not flat:
                    raise RegisterError("max requires at least one value")
                return max(flat)
            return [max(elements) for elements in zip(*args, strict=strict)]
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        flatten = kwargs.get("flatten", True)
        strict = kwargs.get("strict", False)
        if self.vtype in (int, float, bool):
            if flatten:
                flat = [v for iterable in args for v in iterable]
                if not flat:
                    raise RegisterError("range requires at least one value")
                return max(flat) - min(flat)
            return [max(elements) - min(elements) for elements in zip(*args, strict=strict)]
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")
```

## Register and Method Enum Changes

### Method Enum

```python
class Method(int):
    _NAMES: dict[int, str] = {0: "ALL", 1: "SUM", 2: "MAX", 3: "MIN", 4: "RANGE", 5: "MEAN"}
```

### Register Class

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
```

## Exports

### `__init__.py`

```python
from .key import RegisterKey
from .register import Register
from .parameter import Parameter, IterParameter, Id, Code, Name
from .dimension import Dimension, Index, Metric
from .exception import RegisterError, ValidationError, DimensionError

__all__ = [
    "Register",
    "RegisterKey",
    "Parameter",
    "IterParameter",
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

## Dimension (Unchanged)

`Dimension` is not modified in this change. It currently lacks an `id` field and cannot be used as a `RegisterKey`. An `id` field can be added in a future change to make `Dimension` eligible as a Register key.