# Register Slicing & Aggregation API Design

**Date:** 2026-06-30
**Status:** Draft
**Author:** Design Session

## Overview

Add pandas-style slicing and aggregation delegation to Register. The API supports:

```python
reg[Amount][Location, Owner][1, 1] = 1.1          # exact assignment
reg[Amount][Location, Owner][:, :].sum()           # slice → aggregate = 16.5
reg[Amount][Location, Owner][1, :].sum()           # partial slice = 3.3
reg[Amount][Location, Owner][2, [1, 2]].sum()      # list selector = 7.7
reg[Amount][Location, Owner][:, :].agg(Register.SUM)  # method-enum dispatch
```

## Architecture

### Call Chain

```
reg[Amount]                         → KeyView[K]
   [Location, Owner]                → IndexSpace[K]
      [1, 1] = 1.1                  → dict.__setitem__ (exact access)
      [1, 1]                        → 1.1 (exact get)
      [:, :]                        → Selection[K] (slice access)
         .sum(**kwargs)             → key.sum(*values, **kwargs)
         .agg(Method, **kwargs)     → getattr(key, name)(*values, **kwargs)
```

### Class Hierarchy

```
Register[K]
  └── __getitem__(key) → KeyView[K]
        └── __getitem__((Dim1, Dim2)) → IndexSpace[K]
              ├── __getitem__((1, 1)) → value (exact access)
              ├── __setitem__((1, 1), val) → assignment
              └── __getitem__((slice, list)) → Selection[K]
                    ├── .sum(**kwargs) → key.sum(*values, **kwargs)
                    ├── .mean(**kwargs) → key.mean(*values, **kwargs)
                    ├── .min(**kwargs) → key.min(*values, **kwargs)
                    ├── .max(**kwargs) → key.max(*values, **kwargs)
                    ├── .range(**kwargs) → key.range(*values, **kwargs)
                    └── .agg(method, **kwargs) → dispatch by Method enum
```

### Class Responsibilities

| Class | Responsibility |
|-------|---------------|
| **`Register[K]`** | Top-level container. Stores `dict[K, dict[tuple, dict[tuple, Any]]]`. Creates KeyView on access. |
| **`KeyView[K]`** | Scoped to one key (e.g., Amount). Routes dimension tuples to IndexSpace. Replaces `DimensionAsKey`. |
| **`IndexSpace[K]`** | Scoped to one dimension combo (e.g., Location×Owner). Handles exact get/set and detects slices. |
| **`Selection[K]`** | Holds filtered values. Provides `.sum()`, `.mean()`, `.agg()`. Delegates to the key. |

## Data Model

### Register._data

```python
_data: dict[K, dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]]
```

Plain nested dict — no `DimensionAsKey` wrapper class. `KeyView` replaces it as the access layer.

### Access pattern

```python
reg._data[Amount][(Location, Owner)][(1, 1)] == 1.1
```

## Slicing Semantics

### Supported slice elements

| Element | Type | Meaning | Example |
|---------|------|---------|---------|
| `:` | `slice(None, None, None)` | All indices in this dimension | `[:, :]` — everything |
| `1` | `int` | Exact match | `[1, :]` — Location=1, all Owners |
| `[1, 2]` | `list[int]` | In-set match | `[2, [1, 2]]` — Location=2, Owner ∈ {1,2} |
| `1:3` | `slice(1, 3)` | Range match (half-open: 1 ≤ x < 3) | `[1:3, :]` — Location ∈ {1,2} |
| `1:` | `slice(1, None)` | From start onwards (1 ≤ x) | `[1:, :]` — Location ≥ 1 |
| `:3` | `slice(None, 3)` | Up to stop (x < 3) | `[:3, :]` — Location < 3 |

### Detection rule

`IndexSpace.__getitem__` inspects the index tuple:
- **All `int`** → exact access → proxies to underlying dict (`__getitem__` or `__setitem__`)
- **Any `slice` or `list`** → slice access → returns `Selection`

### Resolution algorithm

```python
def _resolve(index: tuple, values: dict[tuple[int, ...], Any]) -> list[Any]:
    results = []
    for idx_tuple, value in values.items():
        if _matches(idx_tuple, index):
            results.append(value)
    return results

def _matches(idx_tuple: tuple[int, ...], pattern: tuple) -> bool:
    for actual, selector in zip(idx_tuple, pattern):
        if isinstance(selector, int):
            if actual != selector:
                return False
        elif isinstance(selector, list):
            if actual not in selector:
                return False
        elif isinstance(selector, slice):
            if selector.start is not None and actual < selector.start:
                return False
            if selector.stop is not None and actual >= selector.stop:
                return False
            # slice(None) matches everything
    return True
```

### Examples

Given data `{(1,1): 1.1, (1,2): 2.2, (2,1): 3.3, (2,2): 4.4, (2,3): 5.5}`:

| Slice | Matched keys | Values | .sum() |
|-------|-------------|--------|--------|
| `[:, :]` | all | [1.1, 2.2, 3.3, 4.4, 5.5] | 16.5 |
| `[1, :]` | (1,1), (1,2) | [1.1, 2.2] | 3.3 |
| `[2, :]` | (2,1), (2,2), (2,3) | [3.3, 4.4, 5.5] | 13.2 |
| `[2, [1, 2]]` | (2,1), (2,2) | [3.3, 4.4] | 7.7 |
| `[1:3, :]` | all (1,2 ∈ range) | [1.1, 2.2, 3.3, 4.4, 5.5] | 16.5 |
| `[:, 1]` | (1,1), (2,1) | [1.1, 3.3] | 4.4 |

## Selection & Aggregation

### Selection class

```python
class Selection(Generic[K]):
    _key: K
    _values: list[Any]

    def __init__(self, key: K, values: list[Any]) -> None:
        self._key = key
        self._values = values

    def sum(self, **kwargs: Any) -> Any:
        return self._key.sum(*self._values, **kwargs)

    def mean(self, **kwargs: Any) -> Any:
        return self._key.mean(*self._values, **kwargs)

    def min(self, **kwargs: Any) -> Any:
        return self._key.min(*self._values, **kwargs)

    def max(self, **kwargs: Any) -> Any:
        return self._key.max(*self._values, **kwargs)

    def range(self, **kwargs: Any) -> Any:
        return self._key.range(*self._values, **kwargs)

    def agg(self, method: Method, **kwargs: Any) -> Any:
        name = _METHOD_NAMES[int(method)]
        fn = getattr(self._key, name)
        return fn(*self._values, **kwargs)
```

### Method dispatch table

```python
_METHOD_NAMES: dict[int, str] = {
    1: "sum",
    2: "max",
    3: "min",
    4: "range",
    5: "mean",
}
```

`ALL` (0) is removed from Register and excluded from `_METHOD_NAMES` — it was a selector wildcard, not an aggregation method. `select()` now uses `None` in the target tuple as the wildcard.

### Delegation flow

```
Selection.sum(**kwargs)
  → self._key.sum(*self._values, **kwargs)
    → ParameterKey.sum(1.1, 2.2, 3.3, 4.4, 5.5)
      → sum(args) = 16.5

Selection.agg(Register.SUM, **kwargs)
  → _METHOD_NAMES[1] = "sum"
  → getattr(key, "sum")(*values, **kwargs)
    → same as above
```

### Config forwarding

`**kwargs` passed to `Selection.sum(**kwargs)` or `Selection.agg(method, **kwargs)` is forwarded directly to the key's aggregation method. The key decides what to do with it.

## RegisterKey ABC Changes

The `data` parameter is removed from all method signatures — it was unused in all implementations:

```python
class RegisterKey(ABC):
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

    @abstractmethod
    def validate(self, *args: Any, **kwargs: Any) -> bool: ...
```

## Key Hierarchy

`ParameterKey` is split into three specialized types, each with clear aggregation support:

```
RegisterKey (ABC, public) — the protocol
└── _BaseKey (private) — shared implementation + NotImplementedError defaults
    ├── NumKey                    # overrides: sum, mean, min, max, range
    ├── StrKey                    # overrides: min, max
    ├── DimensionKey              # overrides: min, max, range
    └── DimensionCollectionKey    # overrides: sum, min, max, range
```

### _BaseKey

Provides identity fields, dunder methods, and default `NotImplementedError` for all aggregation methods. Subclasses override only what they support.

```python
class _BaseKey(RegisterKey):
    """Internal base — not exported."""

    def __init__(self, id: int, name: str, name_cn: str) -> None:
        self._id = id
        self._name = name
        self._name_cn = name_cn

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

    def sum(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(f"sum not supported for {type(self).__name__}")

    def mean(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(f"mean not supported for {type(self).__name__}")

    def min(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(f"min not supported for {type(self).__name__}")

    def max(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(f"max not supported for {type(self).__name__}")

    def range(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(f"range not supported for {type(self).__name__}")
```

### NumKey

For numerical types. `vtype` is dedicated to NumKey — choices are `float`, `int`, `bool`, default `float`.

```python
class NumKey(_BaseKey):
    """Key for numerical values (int, float, bool)."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: type = float) -> None:
        super().__init__(id, name, name_cn)
        if vtype not in (float, int, bool):
            raise RegisterError(f"NumKey vtype must be float, int, or bool, got {vtype}")
        self.vtype = vtype

    def sum(self, *args: Any, **kwargs: Any) -> Any:
        return self.vtype(sum(args))

    def mean(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("mean requires at least one value")
        return sum(args) / len(args)

    def min(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        return min(args)

    def max(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        return max(args)

    def range(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        return max(args) - min(args)

    def validate(self, *args: Any, **kwargs: Any) -> bool:
        return all(isinstance(v, self.vtype) for v in args)
```

### StrKey

For string values. Overrides `min` and `max` (lexicographic). `sum`, `mean`, `range` inherited from `_BaseKey` as `NotImplementedError`.

```python
class StrKey(_BaseKey):
    """Key for string values."""

    def __init__(self, id: int, name: str, name_cn: str) -> None:
        super().__init__(id, name, name_cn)

    def min(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        return min(args)

    def max(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        return max(args)

    def validate(self, *args: Any, **kwargs: Any) -> bool:
        return all(isinstance(v, str) for v in args)
```

### DimensionKey

For dimension reference values (stored as int). Takes a `Dimension` to derive identity. Overrides `min`, `max`, `range`. `sum`, `mean` inherited from `_BaseKey` as `NotImplementedError`.

```python
class DimensionKey(_BaseKey):
    """Key for dimension values (always int)."""

    def __init__(self, id: int, dim: Dimension) -> None:
        super().__init__(id, dim.name, dim.name_cn)
        self._dim = dim

    def min(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        return min(args)

    def max(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        return max(args)

    def range(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        return min(args), max(args)

    def validate(self, *args: Any, reference: Register, **kwargs: Any) -> bool:
        return all(v in reference[Id][self._dim,] for v in args)
```

### DimensionCollectionKey

For collections (iterables) of dimension values. Like DimensionKey but each stored value is a container of dimension IDs. `_iter_type` specifies the container type — choices are `set`, `list`, `tuple`, default `list`.

```python
class DimensionCollectionKey(_BaseKey):
    """Key for collections of dimension values."""

    def __init__(self, id: int, dim: Dimension, iter_type: type = list) -> None:
        super().__init__(id, dim.name, dim.name_cn)
        if iter_type not in (set, list, tuple):
            raise RegisterError(f"iter_type must be set, list, or tuple, got {iter_type}")
        self._dim = dim
        self._iter_type = iter_type

    def sum(self, *args: Any, **kwargs: Any) -> Any:
        all_elements: set[Any] = set()
        for collection in args:
            all_elements.update(collection)
        return self._iter_type(all_elements)

    def min(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        return min(elem for collection in args for elem in collection)

    def max(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        return max(elem for collection in args for elem in collection)

    def range(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        flat = [elem for collection in args for elem in collection]
        return min(flat), max(flat)

    def validate(self, *args: Any, reference: Register, **kwargs: Any) -> bool:
        return all(v in reference[Id][self._dim,] and isinstance(collection, self._iter_type) for collection in args for v in collection)
```

### Aggregation support matrix

| Key Type | vtype | sum | mean | min | max | range |
|----------|-------|-----|------|-----|-----|-------|
| NumKey | int, float, bool (caller specifies) | ✓ | ✓ | ✓ | ✓ | ✓ |
| StrKey | str (fixed) | ✗ | ✗ | ✓ lex | ✓ lex | ✗ |
| DimensionKey | int (fixed) | ✗ | ✗ | ✓ | ✓ | ✓ (min,max) |
| DimensionCollectionKey | int (fixed), _iter_type=set/list/tuple | ✓ union | ✗ | ✓ | ✓ | ✓ (min,max) |

### parameter.py updates

```python
from .key import NumKey, StrKey

Id = NumKey(1, "id", "ID", int)
Code = StrKey(2, "code", "编码")
Name = StrKey(3, "name", "名称")
```

### Validate redesign

Since `data` is removed, `validate` needs a different way to access stored values. Two options:

1. **Keep `data` on `validate` only** — `validate` is semantically different from aggregation (it checks stored data, not selected values). Keep its signature as `validate(self, data, *args, **kwargs)`.
2. **Pass values as `*args`** — call `key.validate(*all_values)` from `Register.validate()`, collecting all stored values for that key.

**Decision:** Option 2 — `Register.validate()` collects all values for each key and passes them as `*args`. This keeps the ABC consistent.

```python
# Register.validate()
def validate(self, **kwargs: Any) -> bool:
    rs = True
    for key in self._data:
        for dims in self._data[key]:
            rs &= key.validate(*self._data[key][dims].values(), **kwargs)
    return rs
```

Validate is simpler now — each key type checks its own vtype directly (see Key Hierarchy section). No more `TypeError` fallback for Dimension instances since `DimensionKey` handles that case explicitly.

## File Layout

```
register/
├── key.py          # RegisterKey, _BaseKey, NumKey, StrKey, DimensionKey, DimensionCollectionKey
│                   # Changed: ParameterKey removed, split into NumKey/StrKey/DimensionKey
│                   #          PositionKey and IterableKey removed
├── register.py     # Register, Method, KeyView, IndexSpace, Selection
│                   # Changed: DimensionAsKey removed, _data is plain nested dict
├── parameter.py    # Updated: Id→NumKey, Code/Name→StrKey
├── dimension.py    # Unchanged
├── exception.py    # Unchanged
└── __init__.py     # Updated exports
```

## Updated Exports

```python
from .key import RegisterKey, NumKey, StrKey, DimensionKey, DimensionCollectionKey
from .register import Register, Method, KeyView, IndexSpace, Selection
from .parameter import Id, Code, Name
from .dimension import Dimension, Index, Metric
from .exception import RegisterError, ValidationError, DimensionError

__all__ = [
    "Register",
    "Method",
    "KeyView",
    "IndexSpace",
    "Selection",
    "RegisterKey",
    "NumKey",
    "StrKey",
    "DimensionKey",
    "DimensionCollectionKey",
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

## Register Class

```python
class Register(Generic[K]):
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    MEAN: Method = Method(5)

    _data: dict[K, dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]]

    def __init__(self) -> None:
        self._data = {}

    def __getitem__(self, key: K) -> KeyView[K]:
        if key not in self._data:
            self._data[key] = {}
        return KeyView(key, self._data[key])

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def select(self, key: K, dimension: tuple[Dimension, ...],
               target: tuple[int | None, ...] | None = None
               ) -> Generator[tuple[int, ...], None, None]:
        for index in self._data[key][dimension]:
            if target is None:
                yield index
            elif all(j is None or i == j for i, j in zip(index, target)):
                yield index

    def validate(self, reference: Register | None = None, **kwargs: Any) -> bool:
        if reference is None:
            reference = self
        rs = True
        for key, dim_data in self._data.items():
            for dims, idx_dict in dim_data.items():
                rs &= key.validate(*idx_dict.values(), reference=reference, **kwargs)
        return rs
```

`ALL` is removed from Register — it was a selector wildcard, not an aggregation method. `select()` now uses `None` in the target tuple as the wildcard: `target = (1, None, 3)` means "match any" at position 2.

## KeyView Class

```python
class KeyView(Generic[K]):
    _key: K
    _data: dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]

    def __init__(self, key: K, data: dict) -> None:
        self._key = key
        self._data = data

    def __getitem__(self, dims: tuple[Dimension, ...]) -> IndexSpace[K]:
        if dims not in self._data:
            self._data[dims] = {}
        return IndexSpace(self._key, self._data[dims])

    def __iter__(self) -> Iterator[tuple[Dimension, ...]]:
        return iter(self._data)

    def __repr__(self) -> str:
        if not self._data:
            return f"KeyView({self._key}, empty)"
        parts = []
        for dim_tuple, idx_dict in self._data.items():
            dim_names = ",".join(repr(d) for d in dim_tuple)
            parts.append(f"({dim_names}): {len(idx_dict)}")
        return f"KeyView({self._key}, {{{', '.join(parts)}}})"

    def pop(self, dims: tuple[Dimension, ...]) -> dict[tuple[int, ...], Any]:
        return self._data.pop(dims, {})
```

## IndexSpace Class

```python
class IndexSpace(Generic[K]):
    _key: K
    _data: dict[tuple[int, ...], Any]

    def __init__(self, key: K, data: dict[tuple[int, ...], Any]) -> None:
        self._key = key
        self._data = data

    def __getitem__(self, index: tuple) -> Any | Selection[K]:
        if _has_slice(index):
            filtered = _resolve(index, self._data)
            return Selection(self._key, filtered)
        return self._data[index]

    def __setitem__(self, index: tuple[int, ...], value: Any) -> None:
        self._data[index] = value

    def __contains__(self, index: tuple[int, ...]) -> bool:
        return index in self._data

    def __repr__(self) -> str:
        return f"IndexSpace({self._key}, {len(self._data)} entries)"


def _has_slice(index: tuple) -> bool:
    """Return True if any element is a slice or list (i.e., not all ints)."""
    if not isinstance(index, tuple):
        index = (index,)
    return any(isinstance(elem, (slice, list)) for elem in index)


def _resolve(index: tuple, values: dict[tuple[int, ...], Any]) -> list[Any]:
    """Filter values by the index pattern, return matching values."""
    if not isinstance(index, tuple):
        index = (index,)
    results = []
    for idx_tuple, value in values.items():
        if _matches(idx_tuple, index):
            results.append(value)
    return results


def _matches(idx_tuple: tuple[int, ...], pattern: tuple) -> bool:
    """Check if an index tuple matches a slice pattern."""
    for actual, selector in zip(idx_tuple, pattern):
        if isinstance(selector, int):
            if actual != selector:
                return False
        elif isinstance(selector, list):
            if actual not in selector:
                return False
        elif isinstance(selector, slice):
            if selector.start is not None and actual < selector.start:
                return False
            if selector.stop is not None and actual >= selector.stop:
                return False
    return True
```

## Summary of Changes from Current Codebase

| Area | Current | New |
|------|---------|-----|
| `DimensionAsKey` | Separate class wrapping inner dict | Removed — replaced by `KeyView` |
| `Register._data` | `dict[K, DimensionAsKey]` via `defaultdict` | `dict[K, dict[tuple, dict[tuple, Any]]]` plain dict |
| `Register.ALL` | `Method(0)` class attribute | Removed — `select()` uses `None` as wildcard |
| `RegisterKey` methods | `(self, data, *args, **kwargs)` | `(self, *args, **kwargs)` — `data` removed |
| `ParameterKey` | One class handling int/float/str/Dimension | Split into `NumKey`, `StrKey`, `DimensionKey` |
| `PositionKey`, `IterableKey` | Tuple and iterable key types | Removed — may be reintroduced later |
| New classes | — | `KeyView`, `IndexSpace`, `Selection` |
| Slicing | Not supported | `int`, `list[int]`, `slice` in index tuples |
| Aggregation dispatch | Not supported | `Selection.agg(method, **kwargs)` |