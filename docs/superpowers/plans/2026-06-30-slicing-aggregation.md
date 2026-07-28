# Slicing & Aggregation API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add pandas-style slicing and aggregation delegation to Register, replacing DimensionAsKey with KeyView/IndexSpace/Selection and splitting ParameterKey into NumKey/StrKey/DimensionKey/DimensionCollectionKey.

**Architecture:** Register stores a plain nested dict `dict[K, dict[tuple[Dimension,...], dict[tuple[int,...], Any]]]`. Access goes through KeyView (per-key) → IndexSpace (per-dimension-combo) → Selection (sliced view). Selection delegates aggregation to the key's methods, which receive the selection dict directly.

**Tech Stack:** Python 3.11+, pytest, mypy strict, ruff

**Spec:** `docs/superpowers/specs/2026-06-30-register-slicing-aggregation-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `register/key.py` | Rewrite | RegisterKey ABC, _BaseKey, NumKey, StrKey, DimensionKey, DimensionCollectionKey |
| `register/register.py` | Rewrite | Register, Method, KeyView, IndexSpace, Selection, slicing helpers |
| `register/parameter.py` | Update | Id→NumKey(int), Code/Name→StrKey |
| `register/__init__.py` | Update | New exports |
| `tests/conftest.py` | Rewrite | Fixtures using new key types |
| `tests/test_key.py` | Rewrite | Tests for all key types |
| `tests/test_register.py` | Rewrite | Tests for Register, KeyView, IndexSpace, Selection |
| `tests/test_parameter.py` | Rewrite | Tests for Id/Code/Name singletons |
| `tests/test_init.py` | Rewrite | Export tests |

---

### Task 1: Rewrite `register/key.py` — ABC and _BaseKey

**Files:**
- Rewrite: `register/key.py`
- Test: `tests/test_key.py`

- [ ] **Step 1: Write failing tests for _BaseKey**

```python
# tests/test_key.py
import pytest
from register.key import _BaseKey, RegisterKey


class ConcreteKey(_BaseKey):
    """Minimal concrete key for testing _BaseKey."""

    pass


class TestBaseKey:
    def test_init(self):
        k = ConcreteKey(1, "test", "测试")
        assert k.id == 1
        assert k.name == "test"
        assert k.name_cn == "测试"

    def test_str_repr(self):
        k = ConcreteKey(1, "test", "测试")
        assert str(k) == "test"
        assert repr(k) == "test"

    def test_hash(self):
        k1 = ConcreteKey(1, "a", "A")
        k2 = ConcreteKey(1, "b", "B")
        assert hash(k1) == hash(k2)

    def test_eq_same_class(self):
        k1 = ConcreteKey(1, "a", "A")
        k2 = ConcreteKey(1, "b", "B")
        assert k1 == k2

    def test_eq_different_id(self):
        k1 = ConcreteKey(1, "a", "A")
        k2 = ConcreteKey(2, "a", "A")
        assert k1 != k2

    def test_eq_different_class(self):
        class OtherKey(_BaseKey):
            pass

        k1 = ConcreteKey(1, "a", "A")
        k2 = OtherKey(1, "a", "A")
        assert k1 != k2

    def test_sum_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="sum not supported"):
            k.sum({})

    def test_mean_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="mean not supported"):
            k.mean({})

    def test_min_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="min not supported"):
            k.min({})

    def test_max_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="max not supported"):
            k.max({})

    def test_range_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="range not supported"):
            k.range({})

    def test_is_register_key(self):
        k = ConcreteKey(1, "a", "A")
        assert isinstance(k, RegisterKey)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -v`
Expected: FAIL — `ImportError: cannot import name '_BaseKey'`

- [ ] **Step 3: Implement RegisterKey ABC and _BaseKey**

```python
# register/key.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .exception import RegisterError


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
    def sum(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def mean(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def range(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def validate(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]: ...


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

    def sum(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"sum not supported for {type(self).__name__}")

    def mean(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"mean not supported for {type(self).__name__}")

    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"min not supported for {type(self).__name__}")

    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"max not supported for {type(self).__name__}")

    def range(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"range not supported for {type(self).__name__}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: add RegisterKey ABC and _BaseKey with NotImplementedError defaults"
```

---

### Task 2: Add NumKey

**Files:**
- Modify: `register/key.py`
- Modify: `tests/test_key.py`

- [ ] **Step 1: Write failing tests for NumKey**

Append to `tests/test_key.py`:

```python
from register.key import NumKey


class TestNumKey:
    def test_init_default_float(self):
        k = NumKey(1, "amount", "件量")
        assert k.vtype is float

    def test_init_int(self):
        k = NumKey(1, "count", "计数", int)
        assert k.vtype is int

    def test_init_bool(self):
        k = NumKey(1, "flag", "标志", bool)
        assert k.vtype is bool

    def test_init_invalid_vtype(self):
        with pytest.raises(RegisterError, match="vtype must be float, int, or bool"):
            NumKey(1, "bad", "坏", str)

    def test_sum_float(self):
        k = NumKey(1, "a", "A", float)
        result = k.sum({(1,): 1.5, (2,): 2.5})
        assert result == 4.0
        assert isinstance(result, float)

    def test_sum_int(self):
        k = NumKey(1, "a", "A", int)
        result = k.sum({(1,): 3, (2,): 7})
        assert result == 10
        assert isinstance(result, int)

    def test_sum_empty(self):
        k = NumKey(1, "a", "A", float)
        result = k.sum({})
        assert result == 0.0

    def test_mean(self):
        k = NumKey(1, "a", "A", float)
        result = k.mean({(1,): 2.0, (2,): 4.0})
        assert result == 3.0

    def test_mean_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="mean requires at least one value"):
            k.mean({})

    def test_min(self):
        k = NumKey(1, "a", "A", float)
        assert k.min({(1,): 3.0, (2,): 1.0}) == 1.0

    def test_min_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="min requires at least one value"):
            k.min({})

    def test_max(self):
        k = NumKey(1, "a", "A", float)
        assert k.max({(1,): 3.0, (2,): 1.0}) == 3.0

    def test_max_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="max requires at least one value"):
            k.max({})

    def test_range(self):
        k = NumKey(1, "a", "A", float)
        assert k.range({(1,): 1.0, (2,): 5.0}) == 4.0

    def test_range_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="range requires at least one value"):
            k.range({})

    def test_validate_pass(self):
        k = NumKey(1, "a", "A", float)
        result = k.validate({(1,): 1.0, (2,): 2.0})
        assert result == {(1,): True, (2,): True}

    def test_validate_fail(self):
        k = NumKey(1, "a", "A", float)
        result = k.validate({(1,): 1.0, (2,): "bad"})
        assert result == {(1,): True, (2,): False}

    def test_validate_int(self):
        k = NumKey(1, "a", "A", int)
        result = k.validate({(1,): 5, (2,): 3.14})
        assert result == {(1,): True, (2,): False}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestNumKey -v`
Expected: FAIL — `ImportError: cannot import name 'NumKey'`

- [ ] **Step 3: Implement NumKey**

Append to `register/key.py`:

```python
class NumKey(_BaseKey):
    """Key for numerical values (int, float, bool)."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: type = float) -> None:
        super().__init__(id, name, name_cn)
        if vtype not in (float, int, bool):
            raise RegisterError(f"NumKey vtype must be float, int, or bool, got {vtype}")
        self.vtype = vtype

    def sum(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        return self.vtype(sum(selection.values()))

    def mean(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("mean requires at least one value")
        return sum(selection.values()) / len(selection)

    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("min requires at least one value")
        return min(selection.values())

    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("max requires at least one value")
        return max(selection.values())

    def range(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("range requires at least one value")
        return max(selection.values()) - min(selection.values())

    def validate(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        return {k: isinstance(v, self.vtype) for k, v in selection.items()}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestNumKey -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: add NumKey with sum/mean/min/max/range and validate"
```

---

### Task 3: Add StrKey

**Files:**
- Modify: `register/key.py`
- Modify: `tests/test_key.py`

- [ ] **Step 1: Write failing tests for StrKey**

Append to `tests/test_key.py`:

```python
from register.key import StrKey


class TestStrKey:
    def test_init(self):
        k = StrKey(1, "name", "名称")
        assert k.id == 1
        assert k.name == "name"

    def test_min(self):
        k = StrKey(1, "a", "A")
        assert k.min({(1,): "banana", (2,): "apple"}) == "apple"

    def test_min_empty(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(RegisterError, match="min requires at least one value"):
            k.min({})

    def test_max(self):
        k = StrKey(1, "a", "A")
        assert k.max({(1,): "banana", (2,): "apple"}) == "banana"

    def test_max_empty(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(RegisterError, match="max requires at least one value"):
            k.max({})

    def test_sum_raises(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(NotImplementedError):
            k.sum({(1,): "a"})

    def test_mean_raises(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(NotImplementedError):
            k.mean({(1,): "a"})

    def test_range_raises(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(NotImplementedError):
            k.range({(1,): "a"})

    def test_validate_pass(self):
        k = StrKey(1, "a", "A")
        result = k.validate({(1,): "hello", (2,): "world"})
        assert result == {(1,): True, (2,): True}

    def test_validate_fail(self):
        k = StrKey(1, "a", "A")
        result = k.validate({(1,): "hello", (2,): 42})
        assert result == {(1,): True, (2,): False}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestStrKey -v`
Expected: FAIL — `ImportError: cannot import name 'StrKey'`

- [ ] **Step 3: Implement StrKey**

Append to `register/key.py`:

```python
class StrKey(_BaseKey):
    """Key for string values."""

    def __init__(self, id: int, name: str, name_cn: str) -> None:
        super().__init__(id, name, name_cn)

    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("min requires at least one value")
        return min(selection.values())

    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("max requires at least one value")
        return max(selection.values())

    def validate(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        return {k: isinstance(v, str) for k, v in selection.items()}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestStrKey -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: add StrKey with min/max and validate"
```

---

### Task 4: Add DimensionKey and DimensionCollectionKey

**Files:**
- Modify: `register/key.py`
- Modify: `tests/test_key.py`

- [ ] **Step 1: Write failing tests for DimensionKey**

Append to `tests/test_key.py`:

```python
from register.key import DimensionKey
from register.dimension import Dimension


class TestDimensionKey:
    def test_init(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.id == 1
        assert k.name == "location"
        assert k.name_cn == "地点"
        assert k._dim is dim

    def test_min(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.min({(1,): 3, (2,): 1}) == 1

    def test_min_empty(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(RegisterError):
            k.min({})

    def test_max(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.max({(1,): 3, (2,): 1}) == 3

    def test_range(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.range({(1,): 1, (2,): 5}) == (1, 5)

    def test_sum_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.sum({(1,): 1})

    def test_mean_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.mean({(1,): 1})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestDimensionKey -v`
Expected: FAIL — `ImportError: cannot import name 'DimensionKey'`

- [ ] **Step 3: Implement DimensionKey**

Append to `register/key.py`:

```python
from .dimension import Dimension


class DimensionKey(_BaseKey):
    """Key for dimension values (always int)."""

    def __init__(self, id: int, dim: Dimension) -> None:
        super().__init__(id, dim.name, dim.name_cn)
        self._dim = dim

    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("min requires at least one value")
        return min(selection.values())

    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("max requires at least one value")
        return max(selection.values())

    def range(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("range requires at least one value")
        return min(selection.values()), max(selection.values())

    def validate(
        self, selection: dict[tuple[int, ...], Any], reference: Any, **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        return {k: v in reference[Id][self._dim,] for k, v in selection.items()}
```

Note: `reference` is typed as `Any` here to avoid circular import with `Register`. The `Id` import will be added in Task 6 when parameter.py is updated. For now, add a forward reference import at the top of key.py:

```python
from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .parameter import Id
```

Actually, `Id` is used at runtime in `validate`, not just for type checking. We need a lazy import:

```python
def validate(
    self, selection: dict[tuple[int, ...], Any], reference: Any, **kwargs: Any
) -> dict[tuple[int, ...], bool]:
    from .parameter import Id

    return {k: v in reference[Id][self._dim,] for k, v in selection.items()}
```

- [ ] **Step 4: Run DimensionKey tests**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestDimensionKey -v`
Expected: All PASS

- [ ] **Step 5: Write failing tests for DimensionCollectionKey**

Append to `tests/test_key.py`:

```python
from register.key import DimensionCollectionKey


class TestDimensionCollectionKey:
    def test_init_default_list(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert k._iter_type is list

    def test_init_set(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim, set)
        assert k._iter_type is set

    def test_init_invalid_type(self):
        dim = Dimension("location", "地点", "L")
        with pytest.raises(RegisterError, match="iter_type must be"):
            DimensionCollectionKey(1, dim, dict)

    def test_min_per_index(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        result = k.min({(1,): [3, 1, 2], (2,): [5, 4]})
        assert result == {(1,): 1, (2,): 4}

    def test_max_per_index(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        result = k.max({(1,): [3, 1, 2], (2,): [5, 4]})
        assert result == {(1,): 3, (2,): 5}

    def test_range_per_index(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        result = k.range({(1,): [3, 1, 2], (2,): [5, 4]})
        assert result == {(1,): (1, 3), (2,): (4, 5)}

    def test_sum_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.sum({(1,): [1, 2]})

    def test_mean_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.mean({(1,): [1, 2]})
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestDimensionCollectionKey -v`
Expected: FAIL — `ImportError: cannot import name 'DimensionCollectionKey'`

- [ ] **Step 7: Implement DimensionCollectionKey**

Append to `register/key.py`:

```python
class DimensionCollectionKey(_BaseKey):
    """Key for collections of dimension values."""

    def __init__(self, id: int, dim: Dimension, iter_type: type = list) -> None:
        super().__init__(id, dim.name, dim.name_cn)
        if iter_type not in (set, list, tuple):
            raise RegisterError(f"iter_type must be set, list, or tuple, got {iter_type}")
        self._dim = dim
        self._iter_type = iter_type

    def min(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], Any]:
        return {k: min(v) for k, v in selection.items()}

    def max(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], Any]:
        return {k: max(v) for k, v in selection.items()}

    def range(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], Any]:
        return {k: (min(v), max(v)) for k, v in selection.items()}

    def validate(
        self, selection: dict[tuple[int, ...], Any], reference: Any, **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        from .parameter import Id

        return {
            k: isinstance(v, self._iter_type)
            and all(elem in reference[Id][self._dim,] for elem in v)
            for k, v in selection.items()
        }
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestDimensionCollectionKey -v`
Expected: All PASS

- [ ] **Step 9: Run all key tests**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -v`
Expected: All PASS

- [ ] **Step 10: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: add DimensionKey and DimensionCollectionKey"
```

---

### Task 5: Rewrite `register/register.py` — Register, KeyView, IndexSpace, Selection

**Files:**
- Rewrite: `register/register.py`
- Test: `tests/test_register.py`

- [ ] **Step 1: Write failing tests for slicing helpers**

```python
# tests/test_register.py
import pytest
from register.register import _has_slice, _matches, _resolve


class TestHasSlice:
    def test_all_ints(self):
        assert _has_slice((1, 2, 3)) is False

    def test_with_slice(self):
        assert _has_slice((1, slice(None))) is True

    def test_with_list(self):
        assert _has_slice((1, [1, 2])) is True

    def test_non_tuple(self):
        assert _has_slice(1) is False

    def test_non_tuple_slice(self):
        assert _has_slice(slice(None)) is True


class TestMatches:
    def test_exact_match(self):
        assert _matches((1, 2), (1, 2)) is True

    def test_exact_no_match(self):
        assert _matches((1, 3), (1, 2)) is False

    def test_list_match(self):
        assert _matches((1, 2), (1, [2, 3])) is True

    def test_list_no_match(self):
        assert _matches((1, 5), (1, [2, 3])) is False

    def test_slice_all(self):
        assert _matches((1, 2), (slice(None), slice(None))) is True

    def test_slice_range_match(self):
        assert _matches((2, 1), (slice(1, 3), slice(None))) is True

    def test_slice_range_no_match(self):
        assert _matches((3, 1), (slice(1, 3), slice(None))) is False

    def test_slice_start_only(self):
        assert _matches((5, 1), (slice(3, None), slice(None))) is True

    def test_slice_stop_only(self):
        assert _matches((2, 1), (slice(None, 3), slice(None))) is True


class TestResolve:
    def test_all(self):
        data = {(1, 1): "a", (1, 2): "b", (2, 1): "c"}
        result = _resolve((slice(None), slice(None)), data)
        assert result == data

    def test_exact_first(self):
        data = {(1, 1): "a", (1, 2): "b", (2, 1): "c"}
        result = _resolve((1, slice(None)), data)
        assert result == {(1, 1): "a", (1, 2): "b"}

    def test_list_second(self):
        data = {(1, 1): "a", (1, 2): "b", (2, 1): "c"}
        result = _resolve((slice(None), [1]), data)
        assert result == {(1, 1): "a", (2, 1): "c"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_register.py -v -k "TestHasSlice or TestMatches or TestResolve"`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement register.py**

```python
# register/register.py
from __future__ import annotations

import logging
from typing import Any, Generic, TypeVar, TYPE_CHECKING

from .dimension import Dimension
from .key import RegisterKey

if TYPE_CHECKING:
    from typing import Generator, Iterator


K = TypeVar("K", bound=RegisterKey)

logger = logging.getLogger("register")


class Method(int):
    _NAMES: dict[int, str] = {0: "ALL", 1: "SUM", 2: "MAX", 3: "MIN", 4: "RANGE", 5: "MEAN"}

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return False
        return int(self) == int(other)

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return True
        return int(self) != int(other)

    def __hash__(self) -> int:
        return super().__hash__()

    def __repr__(self) -> str:
        return self._NAMES.get(int(self), f"Method({int(self)})")


_METHOD_NAMES: dict[int, str] = {
    1: "sum",
    2: "max",
    3: "min",
    4: "range",
    5: "mean",
}


class Selection(Generic[K]):
    _key: K
    _data: dict[tuple[int, ...], Any]

    def __init__(self, key: K, data: dict[tuple[int, ...], Any]) -> None:
        self._key = key
        self._data = data

    def sum(self, **kwargs: Any) -> Any:
        return self._key.sum(self._data, **kwargs)

    def mean(self, **kwargs: Any) -> Any:
        return self._key.mean(self._data, **kwargs)

    def min(self, **kwargs: Any) -> Any:
        return self._key.min(self._data, **kwargs)

    def max(self, **kwargs: Any) -> Any:
        return self._key.max(self._data, **kwargs)

    def range(self, **kwargs: Any) -> Any:
        return self._key.range(self._data, **kwargs)

    def agg(self, method: Method, **kwargs: Any) -> Any:
        name = _METHOD_NAMES[int(method)]
        fn = getattr(self._key, name)
        return fn(self._data, **kwargs)


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

    def update(self, other: dict[tuple[int, ...], Any]) -> None:
        self._data.update(other)

    def __repr__(self) -> str:
        return f"IndexSpace({self._key}, {len(self._data)} entries)"


class KeyView(Generic[K]):
    _key: K
    _data: dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]

    def __init__(
        self, key: K, data: dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]
    ) -> None:
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

    def __repr__(self) -> str:
        if not self._data:
            return "Register(empty)"
        total_cells = 0
        param_summaries = []
        for param, dim_data in self._data.items():
            cell_count = sum(len(idx_dict) for idx_dict in dim_data.values())
            total_cells += cell_count
            param_summaries.append(f"{param}: {cell_count}")
        return f"Register(params={len(self._data)}, cells={total_cells}, {{{', '.join(param_summaries)}}})"

    def select(
        self,
        key: K,
        dimension: tuple[Dimension, ...],
        target: tuple[int | None, ...] | None = None,
    ) -> Generator[tuple[int, ...], None, None]:
        for index in self._data[key][dimension]:
            if target is None:
                yield index
            elif all(j is None or i == j for i, j in zip(index, target)):
                yield index

    def validate(self, **kwargs: Any) -> Register[K]:
        result = Register[K]()
        for key in self._data:
            for dims in self._data[key]:
                result[key][dims].update(key.validate(self._data[key][dims], **kwargs))
        return result


def _has_slice(index: tuple) -> bool:
    if not isinstance(index, tuple):
        index = (index,)
    return any(isinstance(elem, (slice, list)) for elem in index)


def _resolve(index: tuple, data: dict[tuple[int, ...], Any]) -> dict[tuple[int, ...], Any]:
    if not isinstance(index, tuple):
        index = (index,)
    return {k: v for k, v in data.items() if _matches(k, index)}


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
    return True


__all__ = [
    "Register",
    "Method",
    "KeyView",
    "IndexSpace",
    "Selection",
]
```

- [ ] **Step 4: Run slicing helper tests**

Run: `cd D:/github/register && python -m pytest tests/test_register.py -v -k "TestHasSlice or TestMatches or TestResolve"`
Expected: All PASS

- [ ] **Step 5: Write tests for KeyView, IndexSpace, Selection, Register**

Append to `tests/test_register.py`:

```python
from register import Register, NumKey, Dimension


class TestRegister:
    def test_empty(self):
        reg = Register()
        assert repr(reg) == "Register(empty)"

    def test_getitem_auto_init(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        kv = reg[k]
        assert repr(kv) == f"KeyView({k}, empty)"

    def test_contains(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        assert k not in reg
        reg[k]  # auto-init
        assert k in reg

    def test_assign_and_get(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert reg[k][dim,][1,] == 10.0

    def test_repr(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert "params=1" in repr(reg)
        assert "cells=1" in repr(reg)


class TestKeyView:
    def test_getitem_auto_init(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        idx_space = reg[k][dim,]
        assert repr(idx_space) == f"IndexSpace({k}, 0 entries)"

    def test_iter(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1,][1,] = 1.0
        reg[k][d2,][1,] = 2.0
        dims = list(reg[k])
        assert (d1,) in dims
        assert (d2,) in dims

    def test_pop(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        popped = reg[k].pop((dim,))
        assert popped == {(1,): 10.0}
        assert (dim,) not in list(reg[k])


class TestIndexSpace:
    def test_exact_getset(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert reg[k][dim,][1,] == 10.0

    def test_contains(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert (1,) in reg[k][dim,]
        assert (2,) not in reg[k][dim,]

    def test_slice_returns_selection(self):
        from register.register import Selection

        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        reg[k][dim,][2,] = 20.0
        sel = reg[k][dim,][:,]
        assert isinstance(sel, Selection)

    def test_update(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,].update({(1,): 10.0, (2,): 20.0})
        assert reg[k][dim,][1,] == 10.0
        assert reg[k][dim,][2,] == 20.0


class TestSelection:
    def setup_method(self):
        self.reg = Register()
        self.k = NumKey(1, "amount", "件量", float)
        self.dim = Dimension("loc", "地点", "L")
        self.reg[self.k][self.dim,][1,] = 1.0
        self.reg[self.k][self.dim,][2,] = 2.0
        self.reg[self.k][self.dim,][3,] = 3.0

    def test_sum(self):
        assert self.reg[self.k][self.dim,][:,].sum() == 6.0

    def test_mean(self):
        assert self.reg[self.k][self.dim,][:,].mean() == 2.0

    def test_min(self):
        assert self.reg[self.k][self.dim,][:,].min() == 1.0

    def test_max(self):
        assert self.reg[self.k][self.dim,][:,].max() == 3.0

    def test_range(self):
        assert self.reg[self.k][self.dim,][:,].range() == 2.0

    def test_agg_sum(self):
        assert self.reg[self.k][self.dim,][:,].agg(Register.SUM) == 6.0

    def test_agg_mean(self):
        assert self.reg[self.k][self.dim,][:,].agg(Register.MEAN) == 2.0

    def test_partial_slice(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1, d2][1, 1] = 1.0
        reg[k][d1, d2][1, 2] = 2.0
        reg[k][d1, d2][2, 1] = 3.0
        reg[k][d1, d2][2, 2] = 4.0
        assert reg[k][d1, d2][1, :].sum() == 3.0
        assert reg[k][d1, d2][2, :].sum() == 7.0

    def test_list_selector(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1, d2][1, 1] = 1.0
        reg[k][d1, d2][1, 2] = 2.0
        reg[k][d1, d2][2, 1] = 3.0
        reg[k][d1, d2][2, 2] = 4.0
        reg[k][d1, d2][2, 3] = 5.0
        assert reg[k][d1, d2][2, [1, 2]].sum() == 7.0


class TestSelect:
    def test_select_all(self):
        reg = Register()
        k = NumKey(1, "a", "A", int)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10
        reg[k][dim,][2,] = 20
        indices = list(reg.select(k, (dim,)))
        assert (1,) in indices
        assert (2,) in indices

    def test_select_with_target(self):
        reg = Register()
        k = NumKey(1, "a", "A", int)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10
        reg[k][dim,][2,] = 20
        indices = list(reg.select(k, (dim,), target=(1,)))
        assert indices == [(1,)]

    def test_select_with_none_wildcard(self):
        reg = Register()
        k = NumKey(1, "a", "A", int)
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1, d2][1, 1] = 10
        reg[k][d1, d2][1, 2] = 20
        reg[k][d1, d2][2, 1] = 30
        indices = list(reg.select(k, (d1, d2), target=(1, None)))
        assert (1, 1) in indices
        assert (1, 2) in indices
        assert (2, 1) not in indices


class TestValidate:
    def test_validate_returns_register(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 1.0
        reg[k][dim,][2,] = 2.0
        result = reg.validate()
        assert isinstance(result, Register)

    def test_validate_all_valid(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 1.0
        reg[k][dim,][2,] = 2.0
        result = reg.validate()
        assert result[k][dim,][1,] is True
        assert result[k][dim,][2,] is True

    def test_validate_some_invalid(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 1.0
        reg[k][dim,][2,] = "bad"
        result = reg.validate()
        assert result[k][dim,][1,] is True
        assert result[k][dim,][2,] is False
```

- [ ] **Step 6: Run all register tests**

Run: `cd D:/github/register && python -m pytest tests/test_register.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add register/register.py tests/test_register.py
git commit -m "feat: add Register, KeyView, IndexSpace, Selection with slicing"
```

---

### Task 6: Update `parameter.py` and `__init__.py`

**Files:**
- Rewrite: `register/parameter.py`
- Rewrite: `register/__init__.py`
- Rewrite: `tests/test_parameter.py`
- Rewrite: `tests/test_init.py`
- Rewrite: `tests/conftest.py`

- [ ] **Step 1: Rewrite parameter.py**

```python
# register/parameter.py
from .key import NumKey, StrKey

Id = NumKey(1, "id", "ID", int)
Code = StrKey(2, "code", "编码")
Name = StrKey(3, "name", "名称")

__all__ = [
    "Id",
    "Code",
    "Name",
]
```

- [ ] **Step 2: Rewrite __init__.py**

```python
# register/__init__.py
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

- [ ] **Step 3: Rewrite conftest.py**

```python
# tests/conftest.py
import pytest
from register import Register, NumKey, Dimension
from register.parameter import Id


@pytest.fixture
def empty_register():
    """Empty Register instance."""
    return Register()


@pytest.fixture
def sample_register():
    """Register populated with sample data."""
    reg = Register()
    region = Dimension("region", "地区", "REG")
    product = Dimension("product", "产品", "PRD")

    reg[Id][(region, product)][(1, 1)] = 1
    reg[Id][(region, product)][(1, 2)] = 2
    reg[Id][(region, product)][(2, 1)] = 3
    reg[Id][(region, product)][(2, 2)] = 4

    return reg


@pytest.fixture
def sample_dimension():
    """Sample Dimension for testing."""
    return Dimension("test", "测试", "TST")


@pytest.fixture
def sample_num_key():
    """Sample NumKey for testing."""
    return NumKey(100, "test_param", "测试参数", int)


@pytest.fixture
def price_key():
    """Price NumKey with float type."""
    return NumKey(4, "price", "价格", float)
```

- [ ] **Step 4: Rewrite test_parameter.py**

```python
# tests/test_parameter.py
from register.parameter import Id, Code, Name
from register.key import NumKey, StrKey


class TestId:
    def test_is_num_key(self):
        assert isinstance(Id, NumKey)

    def test_id(self):
        assert Id.id == 1

    def test_name(self):
        assert Id.name == "id"

    def test_vtype(self):
        assert Id.vtype is int


class TestCode:
    def test_is_str_key(self):
        assert isinstance(Code, StrKey)

    def test_id(self):
        assert Code.id == 2

    def test_name(self):
        assert Code.name == "code"


class TestName:
    def test_is_str_key(self):
        assert isinstance(Name, StrKey)

    def test_id(self):
        assert Name.id == 3

    def test_name(self):
        assert Name.name == "name"
```

- [ ] **Step 5: Rewrite test_init.py**

```python
# tests/test_init.py
import register


class TestExports:
    def test_register(self):
        assert hasattr(register, "Register")

    def test_method(self):
        assert hasattr(register, "Method")

    def test_key_view(self):
        assert hasattr(register, "KeyView")

    def test_index_space(self):
        assert hasattr(register, "IndexSpace")

    def test_selection(self):
        assert hasattr(register, "Selection")

    def test_register_key(self):
        assert hasattr(register, "RegisterKey")

    def test_num_key(self):
        assert hasattr(register, "NumKey")

    def test_str_key(self):
        assert hasattr(register, "StrKey")

    def test_dimension_key(self):
        assert hasattr(register, "DimensionKey")

    def test_dimension_collection_key(self):
        assert hasattr(register, "DimensionCollectionKey")

    def test_no_parameter_key(self):
        assert not hasattr(register, "ParameterKey")

    def test_no_position_key(self):
        assert not hasattr(register, "PositionKey")

    def test_no_iterable_key(self):
        assert not hasattr(register, "IterableKey")

    def test_no_dimension_as_key(self):
        assert not hasattr(register, "DimensionAsKey")

    def test_all_exports(self):
        expected = {
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
        }
        assert expected == set(register.__all__)
```

- [ ] **Step 6: Run parameter, init, and conftest tests**

Run: `cd D:/github/register && python -m pytest tests/test_parameter.py tests/test_init.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add register/parameter.py register/__init__.py tests/conftest.py tests/test_parameter.py tests/test_init.py
git commit -m "feat: update parameter singletons and exports for new key hierarchy"
```

---

### Task 7: Run full test suite and fix any issues

**Files:**
- All test files

- [ ] **Step 1: Run full test suite**

Run: `cd D:/github/register && python -m pytest tests/ -v`
Expected: All PASS

- [ ] **Step 2: Run mypy**

Run: `cd D:/github/register && python -m mypy register/`
Expected: No errors

- [ ] **Step 3: Run ruff**

Run: `cd D:/github/register && python -m ruff check register/ tests/`
Expected: No errors

- [ ] **Step 4: Fix any issues found**

Fix any test failures, type errors, or lint issues.

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "fix: resolve remaining issues from full test suite run"
```

---

### Task 8: Delete obsolete files and clean up

**Files:**
- Delete: `register/idea.py` (scratch file, not part of the package)

- [ ] **Step 1: Remove idea.py**

```bash
git rm register/idea.py
git commit -m "chore: remove scratch idea.py"
```

- [ ] **Step 2: Verify clean state**

Run: `cd D:/github/register && python -m pytest tests/ -v && python -m mypy register/ && python -m ruff check register/ tests/`
Expected: All green