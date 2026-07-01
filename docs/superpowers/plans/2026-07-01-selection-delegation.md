# Selection Delegation Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor Selection from a closed aggregation dispatcher to a pure delegation proxy using `__getattr__`, and add the `@delegable` decorator for marking proxy-able methods.

**Architecture:** Selection holds a key, dimension context, and filtered data. Method calls are forwarded to the key via `__getattr__`, which checks for a `_register_key_delegable` marker set by `@delegable`. The RegisterKey ABC becomes identity-only — aggregation methods are opt-in per key type.

**Tech Stack:** Python 3.12+, pytest, typing (Protocol, TypeVar)

---

### Task 1: Add `Selected`, `DelegableMethod`, and `@delegable` to key.py

**Files:**
- Modify: `register/key.py:1-8` (imports and top of file)
- Test: `tests/test_key.py`

- [ ] **Step 1: Write tests for `@delegable` decorator**

Add a new test class at the end of `tests/test_key.py`:

```python
class TestDelegable:
    def test_marks_function(self):
        from register.key import delegable
        def my_func(self, selected):
            return None
        decorated = delegable(my_func)
        assert getattr(decorated, '_register_key_delegable', False) is True

    def test_returns_same_function(self):
        from register.key import delegable
        def my_func(self, selected):
            return None
        decorated = delegable(my_func)
        assert decorated is my_func

    def test_unmarked_function_has_no_marker(self):
        def my_func(self, selected):
            return None
        assert getattr(my_func, '_register_key_delegable', False) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_key.py::TestDelegable -v`
Expected: FAIL — `ImportError: cannot import name 'delegable' from 'register.key'`

- [ ] **Step 3: Add imports and type alias to key.py**

At the top of `register/key.py`, update the imports:

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, TypeVar

from .dimension import Dimension
from .exception import RegisterError

Selected = dict[tuple[int, ...], Any]
```

- [ ] **Step 4: Add `DelegableMethod` Protocol and `@delegable` decorator**

Add after the imports, before the `RegisterKey` class:

```python
class DelegableMethod(Protocol):
    """Protocol for a delegable method on a RegisterKey subclass."""
    def __call__(
        self,
        key: RegisterKey,
        selected: Selected,
        *,
        **kwargs: Any,
    ) -> Any: ...


F = TypeVar("F", bound=DelegableMethod)


def delegable(fn: F) -> F:
    """Mark a method as a delegable aggregation function."""
    fn._register_key_delegable = True  # type: ignore[attr-defined]
    return fn
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_key.py::TestDelegable -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Verify existing tests still pass**

Run: `python -m pytest tests/ -q`
Expected: PASS (160 tests — 157 original + 3 new)

- [ ] **Step 7: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: add Selected type alias, DelegableMethod protocol, and @delegable decorator"
```

---

### Task 2: Refactor RegisterKey ABC — remove aggregation methods

**Files:**
- Modify: `register/key.py:10-43` (RegisterKey class)
- Test: `tests/test_key.py`

- [ ] **Step 1: Update RegisterKey ABC**

Replace the `RegisterKey` class in `register/key.py` (lines 10–43) with:

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
        self, selected: Selected, **kwargs: Any
    ) -> dict[tuple[int, ...], bool]: ...
```

This removes `sum`, `mean`, `min`, `max`, `range` from the ABC. Only `id`, `name`, `name_cn`, and `validate` remain as abstract.

- [ ] **Step 2: Run tests to verify they pass**

Run: `python -m pytest tests/ -q`
Expected: PASS — `_BaseKey` still provides concrete implementations, so no subclass breaks.

- [ ] **Step 3: Commit**

```bash
git add register/key.py
git commit -m "refactor: remove aggregation methods from RegisterKey ABC"
```

---

### Task 3: Update `_BaseKey` — add `@delegable`, rename parameter, remove `**kwargs`

**Files:**
- Modify: `register/key.py:46-98` (_BaseKey class)
- Test: `tests/test_key.py`

- [ ] **Step 1: Write test verifying `@delegable` on `_BaseKey` defaults**

Add to `TestBaseKey` in `tests/test_key.py`:

```python
    def test_sum_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.sum, '_register_key_delegable', False) is True

    def test_mean_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.mean, '_register_key_delegable', False) is True

    def test_min_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.range, '_register_key_delegable', False) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_key.py::TestBaseKey::test_sum_is_delegable -v`
Expected: FAIL — `_BaseKey.sum` doesn't have `_register_key_delegable` marker yet.

- [ ] **Step 3: Update `_BaseKey` in key.py**

Replace the `_BaseKey` class (lines 46–98) with:

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

    @delegable
    def sum(self, selected: Selected) -> Any:
        raise NotImplementedError(f"sum not supported for {type(self).__name__}")

    @delegable
    def mean(self, selected: Selected) -> Any:
        raise NotImplementedError(f"mean not supported for {type(self).__name__}")

    @delegable
    def min(self, selected: Selected) -> Any:
        raise NotImplementedError(f"min not supported for {type(self).__name__}")

    @delegable
    def max(self, selected: Selected) -> Any:
        raise NotImplementedError(f"max not supported for {type(self).__name__}")

    @delegable
    def range(self, selected: Selected) -> Any:
        raise NotImplementedError(f"range not supported for {type(self).__name__}")

    def validate(
        self, selected: Selected, **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        raise NotImplementedError(f"validate not supported for {type(self).__name__}")
```

Key changes: `@delegable` on each aggregation method, `selection` → `selected`, `**kwargs` removed from aggregation methods.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_key.py::TestBaseKey -v`
Expected: PASS (all TestBaseKey tests including 5 new delegable tests)

- [ ] **Step 5: Run full suite**

Run: `python -m pytest tests/ -q`
Expected: PASS (165 tests)

- [ ] **Step 6: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "refactor: add @delegable to _BaseKey, rename selection → selected, remove **kwargs"
```

---

### Task 4: Update `NumKey` — add `@delegable`, remove `**kwargs`

**Files:**
- Modify: `register/key.py:101-137` (NumKey class)
- Test: `tests/test_key.py`

- [ ] **Step 1: Write tests verifying `@delegable` on NumKey methods**

Add to `TestNumKey` in `tests/test_key.py`:

```python
    def test_sum_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.sum, '_register_key_delegable', False) is True

    def test_mean_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.mean, '_register_key_delegable', False) is True

    def test_min_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.range, '_register_key_delegable', False) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_key.py::TestNumKey::test_sum_is_delegable -v`
Expected: FAIL — NumKey overrides `_BaseKey.sum` without `@delegable`.

- [ ] **Step 3: Update NumKey in key.py**

Replace the `NumKey` class (lines 101–137) with:

```python
class NumKey(_BaseKey):
    """Key for numerical values (int, float, bool)."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: type = float) -> None:
        super().__init__(id, name, name_cn)
        if vtype not in (float, int, bool):
            raise RegisterError(f"vtype must be float, int, or bool, got {vtype}")
        self.vtype = vtype

    @delegable
    def sum(self, selected: Selected) -> Any:
        return self.vtype(sum(selected.values()))

    @delegable
    def mean(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("mean requires at least one value")
        return sum(selected.values()) / len(selected)

    @delegable
    def min(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return self.vtype(min(selected.values()))

    @delegable
    def max(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return self.vtype(max(selected.values()))

    @delegable
    def range(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("range requires at least one value")
        return self.vtype(max(selected.values()) - min(selected.values()))

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        return {idx: isinstance(v, self.vtype) for idx, v in selected.items()}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_key.py::TestNumKey -v`
Expected: PASS (all TestNumKey tests including 5 new delegable tests)

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "refactor: add @delegable to NumKey, remove **kwargs, use Selected"
```

---

### Task 5: Update `StrKey` — add `@delegable`, remove `**kwargs`

**Files:**
- Modify: `register/key.py:139-158` (StrKey class)
- Test: `tests/test_key.py`

- [ ] **Step 1: Write tests verifying `@delegable` on StrKey methods**

Add to `TestStrKey` in `tests/test_key.py`:

```python
    def test_min_is_delegable(self):
        k = StrKey(1, "a", "A")
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        k = StrKey(1, "a", "A")
        assert getattr(k.max, '_register_key_delegable', False) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_key.py::TestStrKey::test_min_is_delegable -v`
Expected: FAIL

- [ ] **Step 3: Update StrKey in key.py**

Replace the `StrKey` class (lines 139–158) with:

```python
class StrKey(_BaseKey):
    """Key for string values."""

    def __init__(self, id: int, name: str, name_cn: str) -> None:
        super().__init__(id, name, name_cn)

    @delegable
    def min(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return min(selected.values())

    @delegable
    def max(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return max(selected.values())

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        return {k: isinstance(v, str) for k, v in selected.items()}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_key.py::TestStrKey -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "refactor: add @delegable to StrKey, remove **kwargs, use Selected"
```

---

### Task 6: Update `DimensionKey` — add `@delegable`, remove `**kwargs`

**Files:**
- Modify: `register/key.py:161-189` (DimensionKey class)
- Test: `tests/test_key.py`

- [ ] **Step 1: Write tests verifying `@delegable` on DimensionKey methods**

Add to `TestDimensionKey` in `tests/test_key.py`:

```python
    def test_min_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert getattr(k.range, '_register_key_delegable', False) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_key.py::TestDimensionKey::test_min_is_delegable -v`
Expected: FAIL

- [ ] **Step 3: Update DimensionKey in key.py**

Replace the `DimensionKey` class (lines 161–189) with:

```python
class DimensionKey(_BaseKey):
    """Key for dimension values (always int)."""

    def __init__(self, id: int, dim: Dimension) -> None:
        super().__init__(id, dim.name + 'Id', dim.name_cn + 'ID')
        self._dim = dim

    @delegable
    def min(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return min(selected.values())

    @delegable
    def max(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return max(selected.values())

    @delegable
    def range(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("range requires at least one value")
        return min(selected.values()), max(selected.values())

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        from .parameter import Id

        reference = kwargs["reference"]
        return {k: (v,) in reference[Id][self._dim,] for k, v in selected.items()}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_key.py::TestDimensionKey -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "refactor: add @delegable to DimensionKey, remove **kwargs, use Selected"
```

---

### Task 7: Update `DimensionCollectionKey` — add `@delegable`, remove `**kwargs`

**Files:**
- Modify: `register/key.py:192-224` (DimensionCollectionKey class)
- Test: `tests/test_key.py`

- [ ] **Step 1: Write tests verifying `@delegable` on DimensionCollectionKey methods**

Add to `TestDimensionCollectionKey` in `tests/test_key.py`:

```python
    def test_min_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert getattr(k.range, '_register_key_delegable', False) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_key.py::TestDimensionCollectionKey::test_min_is_delegable -v`
Expected: FAIL

- [ ] **Step 3: Update DimensionCollectionKey in key.py**

Replace the `DimensionCollectionKey` class (lines 192–224) with:

```python
class DimensionCollectionKey(_BaseKey):
    """Key for collections of dimension values."""

    def __init__(self, id: int, dim: Dimension, iter_type: type = list) -> None:
        super().__init__(id, dim.name + 'Collection', dim.name_cn + '集合')
        if iter_type not in (set, list, tuple):
            raise RegisterError(f"iter_type must be set, list, or tuple, got {iter_type}")
        self._dim = dim
        self._iter_type = iter_type

    @delegable
    def min(self, selected: Selected) -> Selected:
        return {k: min(v) for k, v in selected.items()}

    @delegable
    def max(self, selected: Selected) -> Selected:
        return {k: max(v) for k, v in selected.items()}

    @delegable
    def range(self, selected: Selected) -> Selected:
        return {k: (min(v), max(v)) for k, v in selected.items()}

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        from .parameter import Id

        reference = kwargs["reference"]
        result: dict[tuple[int, ...], bool] = {}
        for k, v in selected.items():
            if isinstance(v, self._iter_type):
                result[k] = all((elem,) in reference[Id][self._dim,] for elem in v)  # type: ignore[attr-defined]
            else:
                result[k] = False
        return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_key.py::TestDimensionCollectionKey -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "refactor: add @delegable to DimensionCollectionKey, remove **kwargs, use Selected"
```

---

### Task 8: Rewrite `Selection` as `__getattr__` proxy

**Files:**
- Modify: `register/register.py:19-74` (remove Method, _METHOD_NAMES; rewrite Selection)
- Modify: `register/register.py:87-91` (IndexSpace.__getitem__ passes dims)
- Test: `tests/test_register.py`

- [ ] **Step 1: Write tests for the new Selection proxy behavior**

Add new test methods to `TestSelection` in `tests/test_register.py`:

```python
    def test_proxy_delegable_method(self):
        """@delegable method is callable through Selection."""
        assert self.reg[self.k][self.dim,][:,].sum() == 6.0

    def test_proxy_non_delegable_raises(self):
        """Calling a non-@delegable method raises AttributeError."""
        from register import Register, NumKey, Dimension
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 1.0
        sel = reg[k][dim,][:,]
        import pytest
        with pytest.raises(AttributeError, match="has no delegable method"):
            sel.validate()

    def test_proxy_undefined_raises(self):
        """Calling a nonexistent method raises AttributeError."""
        import pytest
        sel = self.reg[self.k][self.dim,][:,]
        with pytest.raises(AttributeError, match="has no delegable method"):
            sel.nonexistent_method()

    def test_proxy_private_raises(self):
        """Accessing _-prefixed attributes raises AttributeError."""
        import pytest
        sel = self.reg[self.k][self.dim,][:,]
        with pytest.raises(AttributeError):
            sel._private_method()

    def test_proxy_concrete_kwargs(self):
        """Delegable method works with concrete keyword arguments via proxy."""
        # NumKey methods don't have extra kwargs, but the proxy passes them through.
        # Verify the proxy works with empty kwargs (baseline).
        assert self.reg[self.k][self.dim,][:,].sum() == 6.0

    def test_selection_repr(self):
        """Selection repr shows key, dims, and entry count."""
        sel = self.reg[self.k][self.dim,][:,]
        r = repr(sel)
        assert "Selection" in r
        assert "3 entries" in r
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_register.py::TestSelection::test_proxy_non_delegable_raises -v`
Expected: FAIL — current Selection has hardcoded methods, no `__getattr__` proxy.

- [ ] **Step 3: Remove `Method` class, `_METHOD_NAMES` dict from register.py**

Delete lines 19–45 of `register/register.py`:

```python
# DELETE these lines:
class Method(int):
    _NAMES: dict[int, str] = {0: "ALL", 1: "SUM", 2: "MAX", 3: "MIN", 4: "RANGE", 5: "MEAN"}
    # ... entire class ...

_METHOD_NAMES: dict[int, str] = {
    1: "sum", 2: "max", 3: "min", 4: "range", 5: "mean",
}
```

- [ ] **Step 4: Rewrite `Selection` class in register.py**

Replace the `Selection` class with:

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
        if not callable(fn) or not getattr(fn, '_register_key_delegable', False):
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

- [ ] **Step 5: Update `IndexSpace.__getitem__` to pass `self._dims` to Selection**

In `register/register.py`, change line 90 from:
```python
        return Selection(self._key, filtered)
```
to:
```python
        return Selection(self._key, self._dims, filtered)
```

IndexSpace already stores `_dims` — only the Selection constructor call needs the extra argument.

- [ ] **Step 6: Remove `Register.SUM`, `MAX`, `MIN`, `RANGE`, `MEAN` class attributes**

Delete lines 154–158 from the `Register` class:

```python
    # DELETE these lines:
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    MEAN: Method = Method(5)
```

- [ ] **Step 7: Remove `Selection` import from test_register.py line 1**

Change line 1 of `tests/test_register.py` from:
```python
from register.register import _has_slice, _matches, _resolve, Selection
```
to:
```python
from register.register import _has_slice, _matches, _resolve
```

- [ ] **Step 8: Remove `.agg()` test methods from test_register.py**

Delete the following test methods from `TestSelection`:
- `test_agg_sum`
- `test_agg_mean`

- [ ] **Step 9: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: PASS — existing `.sum()`, `.mean()`, `.min()`, `.max()`, `.range()` tests pass via proxy. New proxy tests pass. `.agg()` tests removed.

- [ ] **Step 10: Commit**

```bash
git add register/register.py tests/test_register.py
git commit -m "refactor: rewrite Selection as __getattr__ proxy, remove Method class and .agg()"
```

---

### Task 9: Update `__init__.py` exports

**Files:**
- Modify: `register/__init__.py`
- Test: `tests/test_init.py`

- [ ] **Step 1: Update test_init.py — remove Method, add delegable and Selected**

In `tests/test_init.py`, make these changes:

Remove `test_method` and replace with `test_delegable` and `test_selected`:

```python
    def test_delegable(self):
        assert hasattr(register, "delegable")

    def test_selected(self):
        assert hasattr(register, "Selected")
```

Update `test_all_exports` — replace `"Method"` with `"delegable"` and `"Selected"`:

```python
    def test_all_exports(self):
        expected = {
            "Register", "KeyView", "IndexSpace", "Selection",
            "RegisterKey", "NumKey", "StrKey", "DimensionKey", "DimensionCollectionKey",
            "delegable", "Selected",
            "Dimension", "Index", "Metric",
            "Id", "Code", "Name",
            "RegisterError", "ValidationError", "DimensionError",
        }
        assert expected == set(register.__all__)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_init.py -v`
Expected: FAIL — `delegable` and `Selected` not yet exported, `Method` still exported.

- [ ] **Step 3: Update `__init__.py`**

Replace the contents of `register/__init__.py` with:

```python
from .key import RegisterKey, NumKey, StrKey, DimensionKey, DimensionCollectionKey, delegable, Selected
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
    "Selected",
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

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_init.py -v`
Expected: PASS

- [ ] **Step 5: Run full test suite**

Run: `python -m pytest tests/ -q`
Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add register/__init__.py tests/test_init.py
git commit -m "refactor: update exports — remove Method, add delegable and Selected"
```