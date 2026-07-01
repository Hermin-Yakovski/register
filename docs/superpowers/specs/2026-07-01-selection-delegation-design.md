# Selection Delegation Refactor

**Date:** 2026-07-01
**Status:** Draft
**Author:** Design Session

## Overview

Refactor `Selection` from a closed aggregation dispatcher to a pure delegation proxy. The `__getattr__` mechanism forwards any method call to the underlying key, injecting the data context automatically. This solves two problems:

1. **Boilerplate**: New `RegisterKey` types no longer need to implement (or inherit `NotImplementedError` for) aggregation methods they don't support.
2. **Closed aggregation set**: Key types can define custom aggregation methods (e.g., `MatrixKey.tr()`) that are automatically available through `Selection` without changes to the `Selection` class.

## Architecture

### Delegation Flow

```
sel.sum()
  ↓
Selection.__getattr__('sum')          # 'sum' not found on Selection
  ↓
fn = getattr(self._key, 'sum')        # look up on key (e.g., NumKey)
  ↓
wrapper(**kwargs) → fn(self._data, **kwargs)  # call with data bound
  ↓
NumKey.sum(self._data, **kwargs) → result
```

For custom methods:
```
sel.tr()
  ↓
Selection.__getattr__('tr')           # 'tr' not found on Selection
  ↓
fn = getattr(self._key, 'tr')         # look up on MatrixKey
  ↓
wrapper(**kwargs) → fn(self._data, **kwargs)
  ↓
MatrixKey.tr(self._data, **kwargs) → result
```

For non-delegable methods:
```
sel.sum()   # on MatrixKey with no @delegable sum
  ↓
Selection.__getattr__('sum')
  ↓
fn = getattr(self._key, 'sum')        # found, but _delegable is False
  ↓
AttributeError: "MatrixKey has no delegable method 'sum'"
```

## Selection Redesign

`Selection` holds three fields: the key, the dimension context, and the filtered data. All method calls are proxied to the key via `__getattr__`.

```python
class Selection(Generic[K]):
    _key: K
    _dims: tuple[Dimension, ...]
    _data: dict[tuple[int, ...], Any]

    def __init__(self, key: K, dims: tuple[Dimension, ...], data: dict[tuple[int, ...], Any]) -> None:
        self._key = key
        self._dims = dims
        self._data = data

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            raise AttributeError(name)
        fn = getattr(self._key, name)
        if not callable(fn) or not getattr(fn, '_delegable', False):
            raise AttributeError(
                f"{type(self._key).__name__} has no delegable method '{name}'"
            )
        def wrapper(**kwargs: Any) -> Any:
            return fn(self._data, **kwargs)
        return wrapper

    def __repr__(self) -> str:
        dim_names = ",".join(repr(d) for d in self._dims)
        return f"Selection({self._key}, ({dim_names}), {len(self._data)} entries)"
```

### What's removed

- `.sum()`, `.mean()`, `.min()`, `.max()`, `.range()` — no longer hardcoded
- `.agg(method)` — no longer needed

### What's added

- `_dims: tuple[Dimension, ...]` — dimension context, passed from `IndexSpace`
- `__getattr__` — delegation proxy
- `__repr__` — for debugging

### IndexSpace change

`IndexSpace.__getitem__` passes `self._dims` when creating a `Selection`:

```python
def __getitem__(self, index: tuple[Any, ...]) -> Any | Selection[K]:
    if _has_slice(index):
        filtered = _resolve(index, self._data)
        return Selection(self._key, self._dims, filtered)
    return self._data[index]
```

## @delegable Decorator

The `@delegable` decorator marks methods as aggregation functions that `Selection` can proxy. Only methods with this marker are accessible through `Selection.__getattr__`.

### Definition

```python
from typing import Callable

def delegable(fn: Callable) -> Callable:
    """Mark a method as a delegable aggregation function.

    Delegable methods follow the signature:
        def method(self, selected: dict[tuple[int, ...], Any], *, ...) -> Any
    """
    fn._delegable = True
    return fn
```

### Delegable method signature

Every delegable method must follow this pattern:

```python
@delegable
def method(self, selected: dict[tuple[int, ...], Any], *, param1: type1, param2: type2 = default) -> ReturnType:
    ...
```

- `self` — the key instance
- `selected` — the filtered data dict, injected by `Selection`'s proxy
- `*` — forces all subsequent parameters to be keyword-only
- Concrete keyword-only parameters — no `**kwargs`; every parameter is named and typed
- Return type — explicitly annotated

### Where it lives

`delegable` is defined in `key.py` and exported from the package. Both internal key types (`_BaseKey` subclasses) and external key types use it.

## RegisterKey ABC Redesign

`RegisterKey` becomes an identity-only protocol. Aggregation methods are no longer part of the contract.

```python
class RegisterKey(ABC):
    """Public protocol for any class used as a key in Register[K]."""

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
    def validate(
        self, selected: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]: ...
```

### What's removed from the ABC

- `sum`, `mean`, `min`, `max`, `range` — no longer abstract methods

### What stays

- `id`, `name`, `name_cn` — identity properties
- `validate` — every key type must define how to validate its values

### Rationale

Aggregation methods are an implementation choice, not a contract requirement. A `MatrixKey` doesn't have `sum` — forcing it to declare one violates the interface's purpose. `validate` stays because it's fundamental: every key type must know what constitutes a valid value.

## _BaseKey (Internal)

`_BaseKey` remains internal to the package and not exported. It provides `NotImplementedError` defaults for the standard 5 methods as a convenience for the package's own key types.

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
        return hash((type(self).__name__, self._id, self._name))

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, self.__class__)
                and self._id == getattr(other, "_id", None)
                and self._name == getattr(other, "_name", None))

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn

    # Standard aggregation defaults — convenience, not obligation
    @delegable
    def sum(self, selected: dict[tuple[int, ...], Any]) -> Any:
        raise NotImplementedError(f"sum not supported for {type(self).__name__}")

    @delegable
    def mean(self, selected: dict[tuple[int, ...], Any]) -> Any:
        raise NotImplementedError(f"mean not supported for {type(self).__name__}")

    @delegable
    def min(self, selected: dict[tuple[int, ...], Any]) -> Any:
        raise NotImplementedError(f"min not supported for {type(self).__name__}")

    @delegable
    def max(self, selected: dict[tuple[int, ...], Any]) -> Any:
        raise NotImplementedError(f"max not supported for {type(self).__name__}")

    @delegable
    def range(self, selected: dict[tuple[int, ...], Any]) -> Any:
        raise NotImplementedError(f"range not supported for {type(self).__name__}")

    def validate(
        self, selected: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        raise NotImplementedError(f"validate not supported for {type(self).__name__}")
```

## External Key Types

External key types (e.g., `MatrixKey` defined outside the `register` package) inherit `RegisterKey` directly. They use `@delegable` to mark aggregation methods with concrete kwargs:

```python
from register import RegisterKey, delegable

class MatrixKey(RegisterKey):
    def __init__(self, id: int, name: str, name_cn: str):
        self._id = id
        self._name = name
        self._name_cn = name_cn

    @property
    def id(self): return self._id
    @property
    def name(self): return self._name
    @property
    def name_cn(self): return self._name_cn

    def validate(self, selected: dict[tuple[int, ...], Any], **kwargs: Any) -> dict[tuple[int, ...], bool]:
        return {k: isinstance(v, np.ndarray) for k, v in selected.items()}

    @delegable
    def tr(self, selected: dict[tuple[int, ...], Any]) -> float:
        return sum(v.trace() for v in selected.values())

    @delegable
    def det(self, selected: dict[tuple[int, ...], Any], *, method: str = "lu") -> dict[tuple[int, ...], float]:
        return {k: np.linalg.det(v) for k, v in selected.items()}
    # No sum, mean, min, max, range — AttributeError if called via Selection
```

Usage:
```python
sel = reg[MatrixKey][dims][:, :]
sel.tr()                  # works — delegable, proxied to MatrixKey.tr
sel.det(method="qr")      # works — delegable with concrete kwarg
sel.sum()                 # AttributeError — no delegable 'sum' on MatrixKey
```

## Method Class and .agg() Removal

With `Selection` proxying all method calls to the key, the `Method` class and `.agg()` dispatch become unnecessary.

### Removed

- `Method` class (the `int` subclass with `_NAMES`)
- `Selection.agg()` method
- `_METHOD_NAMES` module-level dict
- `Register.SUM`, `Register.MAX`, `Register.MIN`, `Register.RANGE`, `Register.MEAN` class attributes

### Migration

| Before | After |
|--------|-------|
| `sel.agg(Register.SUM)` | `sel.sum()` |
| `sel.agg(Register.MEAN)` | `sel.mean()` |
| `sel.agg(Register.MIN, x=1)` | `sel.min(x=1)` |
| `sel.agg(Register.MAX)` | `sel.max()` |
| `sel.agg(Register.RANGE)` | `sel.range()` |

## Parameter Rename: `selection` → `selected`

The parameter name `selection` is renamed to `selected` across all key methods:

- `RegisterKey.validate(self, selected, ...)`
- `_BaseKey.sum(self, selected, ...)` and all other defaults
- `NumKey.sum(self, selected, ...)`, `NumKey.mean(...)`, etc.
- `StrKey.min(self, selected, ...)`, `StrKey.max(...)`
- `DimensionKey.min(...)`, `DimensionKey.max(...)`, `DimensionKey.range(...)`
- `DimensionCollectionKey.min(...)`, `DimensionCollectionKey.max(...)`, `DimensionCollectionKey.range(...)`

The `Selection.__getattr__` proxy passes `self._data` as the first positional argument, so the key methods receive it as `selected` regardless of the proxy's internal naming.

## Existing Key Types

No logic changes — only the parameter rename.

### NumKey

```python
class NumKey(_BaseKey):
    def __init__(self, id: int, name: str, name_cn: str, vtype: type = float) -> None:
        super().__init__(id, name, name_cn)
        if vtype not in (float, int, bool):
            raise RegisterError(f"vtype must be float, int, or bool, got {vtype}")
        self.vtype = vtype

    @delegable
    def sum(self, selected: dict[tuple[int, ...], Any]) -> Any:
        return self.vtype(sum(selected.values()))

    @delegable
    def mean(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("mean requires at least one value")
        return sum(selected.values()) / len(selected)

    @delegable
    def min(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return self.vtype(min(selected.values()))

    @delegable
    def max(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return self.vtype(max(selected.values()))

    @delegable
    def range(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("range requires at least one value")
        return self.vtype(max(selected.values()) - min(selected.values()))

    def validate(self, selected: dict[tuple[int, ...], Any], **kwargs: Any) -> dict[tuple[int, ...], bool]:
        return {idx: isinstance(v, self.vtype) for idx, v in selected.items()}
```

### StrKey

```python
class StrKey(_BaseKey):
    @delegable
    def min(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return min(selected.values())

    @delegable
    def max(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return max(selected.values())

    def validate(self, selected: dict[tuple[int, ...], Any], **kwargs: Any) -> dict[tuple[int, ...], bool]:
        return {k: isinstance(v, str) for k, v in selected.items()}
```

### DimensionKey

```python
class DimensionKey(_BaseKey):
    def __init__(self, id: int, dim: Dimension) -> None:
        super().__init__(id, dim.name + 'Id', dim.name_cn + 'ID')
        self._dim = dim

    @delegable
    def min(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return min(selected.values())

    @delegable
    def max(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return max(selected.values())

    @delegable
    def range(self, selected: dict[tuple[int, ...], Any]) -> Any:
        if not selected:
            raise RegisterError("range requires at least one value")
        return min(selected.values()), max(selected.values())

    def validate(self, selected: dict[tuple[int, ...], Any], **kwargs: Any) -> dict[tuple[int, ...], bool]:
        from .parameter import Id
        reference = kwargs["reference"]
        return {k: (v,) in reference[Id][self._dim,] for k, v in selected.items()}
```

### DimensionCollectionKey

```python
class DimensionCollectionKey(_BaseKey):
    def __init__(self, id: int, dim: Dimension, iter_type: type = list) -> None:
        super().__init__(id, dim.name + 'Collection', dim.name_cn + '集合')
        if iter_type not in (set, list, tuple):
            raise RegisterError(f"iter_type must be set, list, or tuple, got {iter_type}")
        self._dim = dim
        self._iter_type = iter_type

    @delegable
    def min(self, selected: dict[tuple[int, ...], Any]) -> dict[tuple[int, ...], Any]:
        return {k: min(v) for k, v in selected.items()}

    @delegable
    def max(self, selected: dict[tuple[int, ...], Any]) -> dict[tuple[int, ...], Any]:
        return {k: max(v) for k, v in selected.items()}

    @delegable
    def range(self, selected: dict[tuple[int, ...], Any]) -> dict[tuple[int, ...], Any]:
        return {k: (min(v), max(v)) for k, v in selected.items()}

    def validate(self, selected: dict[tuple[int, ...], Any], **kwargs: Any) -> dict[tuple[int, ...], bool]:
        from .parameter import Id
        reference = kwargs["reference"]
        result: dict[tuple[int, ...], bool] = {}
        for k, v in selected.items():
            if isinstance(v, self._iter_type):
                result[k] = all((elem,) in reference[Id][self._dim,] for elem in v)
            else:
                result[k] = False
        return result
```

## File Layout

```
register/
├── key.py          # RegisterKey: remove sum/mean/min/max/range from ABC
│                   # delegable: new decorator function
│                   # _BaseKey: parameter rename selection → selected, add @delegable
│                   # NumKey/StrKey/DimensionKey/DimensionCollectionKey: @delegable, remove **kwargs
├── register.py     # Selection: rewrite as __getattr__ proxy, add _dims, check _delegable
│                   # Method class: removed
│                   # _METHOD_NAMES dict: removed
│                   # Register: remove SUM/MAX/MIN/RANGE/MEAN class attributes
│                   # IndexSpace: pass self._dims when creating Selection
├── parameter.py    # Unchanged
├── dimension.py    # Unchanged
├── exception.py    # Unchanged
└── __init__.py     # Remove Method, add delegable to imports and __all__
```

## Exports

```python
from .key import RegisterKey, NumKey, StrKey, DimensionKey, DimensionCollectionKey, delegable
from .register import Register, KeyView, IndexSpace, Selection
from .parameter import Id, Code, Name
from .dimension import Dimension, Index, Metric
from .exception import RegisterError, ValidationError, DimensionError

__all__ = [
    "Register",
    "KeyView",
    "IndexSpace",
    "Selection",
    "RegisterKey",
    "NumKey",
    "StrKey",
    "DimensionKey",
    "DimensionCollectionKey",
    "delegable",
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

`Method` is removed from all exports. `delegable` is added.

## Test Impact

### Tests to remove

- `test_register.py`: `TestSelection.test_agg_sum`, `TestSelection.test_agg_mean`

### Tests to update

- `test_register.py`: Remove `Method` and `Selection` from imports (line 1)
- `test_init.py`: Remove `Method` from expected exports, add `delegable`
- `test_key.py`: Rename `selection` → `selected` in all key method test calls, remove `**kwargs` from test calls

### Tests that stay the same

- All `TestRegister`, `TestKeyView`, `TestIndexSpace` tests — access chain unchanged
- `TestSelection.test_sum`, `test_mean`, `test_min`, `test_max`, `test_range` — still work via proxy
- `TestSelection.test_partial_slice`, `test_list_selector` — proxy doesn't affect slicing
- `TestHasSlice`, `TestMatches`, `TestResolve` — helper functions unchanged
- `TestValidate` — validate logic unchanged
- `test_dimension.py`, `test_parameter.py`, `test_exception.py` — untouched

### New tests to add

- `TestSelection.test_proxy_delegable_method` — a `@delegable` method is callable through Selection
- `TestSelection.test_proxy_non_delegable_raises` — calling a non-`@delegable` method raises `AttributeError`
- `TestSelection.test_proxy_undefined_raises` — calling a nonexistent method raises `AttributeError`
- `TestSelection.test_proxy_private_raises` — `_`-prefixed attributes are not proxied
- `TestSelection.test_proxy_concrete_kwargs` — delegable method accepts concrete keyword arguments
- `TestDelegable.test_marks_function` — `@delegable` sets `_delegable = True` on the function