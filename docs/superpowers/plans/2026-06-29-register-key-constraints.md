# RegisterKey Constraints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a RegisterKey ABC that constrains Register key types to provide identity fields, five aggregation methods, and a validate method — with three concrete implementations: ParameterKey (scalar), PositionKey (fixed-arity tuples), and IterableKey (variable-length iterables).

**Architecture:** `RegisterKey` (public ABC) defines the protocol. `_BaseKey` (private) provides shared identity fields and dunder methods. Three concrete classes (`ParameterKey`, `PositionKey`, `IterableKey`) inherit from `_BaseKey` and implement type-specific aggregation and validation. All key classes live in a new `register/key.py`. The `Method` enum gains `MEAN`. `Register.validate()` delegates to each key's `validate(data)`.

**Tech Stack:** Python 3.11+, pytest, mypy (strict), ruff

**Spec:** `docs/superpowers/specs/2026-06-29-register-key-constraints-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `register/key.py` | Create | RegisterKey ABC, _BaseKey, ParameterKey, PositionKey, IterableKey |
| `register/register.py` | Modify | Bounded TypeVar, MEAN method, Register.validate() |
| `register/parameter.py` | Modify | Slim to ParameterKey singletons (Id, Code, Name) |
| `register/__init__.py` | Modify | Updated exports |
| `tests/conftest.py` | Modify | Fixtures use ParameterKey instead of Parameter |
| `tests/test_key.py` | Create | Tests for RegisterKey, _BaseKey, ParameterKey, PositionKey, IterableKey |
| `tests/test_register.py` | Modify | Tests for MEAN method, Register.validate(), bounded K |

---

### Task 1: RegisterKey ABC and _BaseKey

**Files:**
- Create: `register/key.py`
- Create: `tests/test_key.py`

- [ ] **Step 1: Write tests for RegisterKey and _BaseKey**

Create `tests/test_key.py`:

```python
import pytest
from register.key import RegisterKey, ParameterKey, PositionKey, IterableKey


class TestRegisterKey:
    """RegisterKey is an ABC — cannot be instantiated directly."""

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            RegisterKey()

    def test_subclass_must_implement_all_abstract(self):
        class IncompleteKey(RegisterKey):
            pass

        with pytest.raises(TypeError):
            IncompleteKey()


class TestBaseKeyViaParameterKey:
    """_BaseKey is private; test its behavior through ParameterKey."""

    def test_id_property(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p.id == 1

    def test_name_property(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p.name == "age"

    def test_name_cn_property(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p.name_cn == "年龄"

    def test_str(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert str(p) == "age"

    def test_repr(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert repr(p) == "age"

    def test_hash_based_on_id(self):
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(1, "different", "不同", str)
        assert hash(p1) == hash(p2)

    def test_eq_same_class_same_id(self):
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(1, "age", "年龄", int)
        assert p1 == p2

    def test_eq_same_class_different_id(self):
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(2, "name", "名称", str)
        assert p1 != p2

    def test_eq_different_class_same_id(self):
        p = ParameterKey(1, "x", "X", int)
        pos = PositionKey(1, "x", "X", int, arity=2)
        assert p != pos

    def test_eq_with_non_key_object(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p != "not a key"
        assert p != 1

    def test_vtype_defaults_to_none(self):
        p = ParameterKey(1, "x", "X")
        assert p.vtype is None

    def test_isinstance_register_key(self):
        p = ParameterKey(1, "x", "X", int)
        assert isinstance(p, RegisterKey)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'register.key'`

- [ ] **Step 3: Create `register/key.py` with RegisterKey ABC and _BaseKey**

```python
from __future__ import annotations

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

Note: `ParameterKey`, `PositionKey`, and `IterableKey` are referenced in the tests but not yet defined. The tests that use them will fail at import time. We'll add stub classes in the next step so Task 1 tests pass.

- [ ] **Step 4: Add stub classes so imports work**

Add to the bottom of `register/key.py`:

```python
class ParameterKey(_BaseKey):
    """Key for scalar values."""

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError


class PositionKey(_BaseKey):
    """Key for positional values — tuples of the same length."""

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError


class IterableKey(_BaseKey):
    """Key for iterable values — variable-length collections of vtype."""

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError
```

- [ ] **Step 5: Run tests to verify Task 1 tests pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestRegisterKey tests/test_key.py::TestBaseKeyViaParameterKey -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: add RegisterKey ABC and _BaseKey with stub subclasses"
```

---

### Task 2: ParameterKey Aggregation

**Files:**
- Modify: `register/key.py` (replace ParameterKey stub)
- Modify: `tests/test_key.py` (add ParameterKey tests)

- [ ] **Step 1: Write tests for ParameterKey.sum**

Add to `tests/test_key.py`:

```python
from register.register import DimensionAsKey


class TestParameterKeySum:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_sum_int(self):
        k = self._make_key(int)
        assert k.sum(DimensionAsKey(), 1, 2, 3) == 6

    def test_sum_float(self):
        k = self._make_key(float)
        assert k.sum(DimensionAsKey(), 1.5, 2.5) == 4.0

    def test_sum_bool(self):
        k = self._make_key(bool)
        assert k.sum(DimensionAsKey(), True, False, True) == 2

    def test_sum_int_empty(self):
        k = self._make_key(int)
        assert k.sum(DimensionAsKey()) == 0

    def test_sum_str(self):
        k = self._make_key(str)
        result = k.sum(DimensionAsKey(), "a", "b", "a", "c")
        assert result == {"a": 2, "b": 1, "c": 1}

    def test_sum_str_empty(self):
        k = self._make_key(str)
        assert k.sum(DimensionAsKey()) == {}

    def test_sum_dimension(self):
        from register.dimension import Dimension
        d1 = Dimension("r1", "区域1", "R1")
        d2 = Dimension("r2", "区域2", "R2")
        k = ParameterKey(1, "test", "测试", d1)
        result = k.sum(DimensionAsKey(), d1, d2, d1)
        assert result == {d1: 2, d2: 1}

    def test_sum_unsupported_vtype(self):
        k = self._make_key(list)
        with pytest.raises(NotImplementedError):
            k.sum(DimensionAsKey(), [1], [2])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestParameterKeySum -v`
Expected: FAIL — `NotImplementedError`

- [ ] **Step 3: Implement ParameterKey.sum**

Replace the `ParameterKey` stub in `register/key.py` with:

```python
class ParameterKey(_BaseKey):
    """Key for scalar values."""

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if self.vtype in (int, float, bool):
            return sum(args)
        elif self.vtype is str or isinstance(self.vtype, Dimension):
            from collections import Counter
            return dict(Counter(args))
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError
```

Also add the `Dimension` import at the top of `key.py`:

```python
from .dimension import Dimension
```

- [ ] **Step 4: Run tests to verify sum passes**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestParameterKeySum -v`
Expected: All PASS

- [ ] **Step 5: Write tests for ParameterKey.mean, min, max, range**

Add to `tests/test_key.py`:

```python
class TestParameterKeyMean:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_mean_int(self):
        k = self._make_key(int)
        assert k.mean(DimensionAsKey(), 2, 4, 6) == 4.0

    def test_mean_float(self):
        k = self._make_key(float)
        assert k.mean(DimensionAsKey(), 1.0, 3.0) == 2.0

    def test_mean_bool(self):
        k = self._make_key(bool)
        assert k.mean(DimensionAsKey(), True, False, True) == pytest.approx(2 / 3)

    def test_mean_empty_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.mean(DimensionAsKey())

    def test_mean_str_not_implemented(self):
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.mean(DimensionAsKey(), "a", "b")


class TestParameterKeyMin:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_min_int(self):
        k = self._make_key(int)
        assert k.min(DimensionAsKey(), 3, 1, 2) == 1

    def test_min_float(self):
        k = self._make_key(float)
        assert k.min(DimensionAsKey(), 3.5, 1.5, 2.5) == 1.5

    def test_min_bool(self):
        k = self._make_key(bool)
        assert k.min(DimensionAsKey(), True, False, True) is False

    def test_min_str(self):
        k = self._make_key(str)
        assert k.min(DimensionAsKey(), "banana", "apple", "cherry") == "apple"

    def test_min_empty_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.min(DimensionAsKey())

    def test_min_dimension_not_implemented(self):
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.min(DimensionAsKey(), d)


class TestParameterKeyMax:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_max_int(self):
        k = self._make_key(int)
        assert k.max(DimensionAsKey(), 3, 1, 2) == 3

    def test_max_float(self):
        k = self._make_key(float)
        assert k.max(DimensionAsKey(), 3.5, 1.5, 2.5) == 3.5

    def test_max_bool(self):
        k = self._make_key(bool)
        assert k.max(DimensionAsKey(), True, False, True) is True

    def test_max_str(self):
        k = self._make_key(str)
        assert k.max(DimensionAsKey(), "banana", "apple", "cherry") == "cherry"

    def test_max_empty_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.max(DimensionAsKey())

    def test_max_dimension_not_implemented(self):
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.max(DimensionAsKey(), d)


class TestParameterKeyRange:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_range_int(self):
        k = self._make_key(int)
        assert k.range(DimensionAsKey(), 3, 1, 5) == 4

    def test_range_float(self):
        k = self._make_key(float)
        assert k.range(DimensionAsKey(), 3.5, 1.5, 2.5) == 2.0

    def test_range_bool(self):
        k = self._make_key(bool)
        assert k.range(DimensionAsKey(), True, False) == 1

    def test_range_empty_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.range(DimensionAsKey())

    def test_range_str_not_implemented(self):
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), "a", "b")

    def test_range_dimension_not_implemented(self):
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), d)
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -k "TestParameterKeyMean or TestParameterKeyMin or TestParameterKeyMax or TestParameterKeyRange" -v`
Expected: FAIL — `NotImplementedError` on mean/min/max/range calls

- [ ] **Step 7: Implement ParameterKey.mean, min, max, range**

Replace the remaining stubs in `ParameterKey` within `register/key.py`:

```python
    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("mean requires at least one value")
        if self.vtype in (int, float, bool):
            return sum(args) / len(args)
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        if self.vtype in (int, float, bool, str):
            return min(args)
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        if self.vtype in (int, float, bool, str):
            return max(args)
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        if self.vtype in (int, float, bool):
            return max(args) - min(args)
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")
```

Add the `RegisterError` import at the top of `key.py`:

```python
from .exception import RegisterError
```

- [ ] **Step 8: Run all ParameterKey tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -k "ParameterKey" -v`
Expected: All PASS

- [ ] **Step 9: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: implement ParameterKey aggregation methods (sum, mean, min, max, range)"
```

---

### Task 3: PositionKey

**Files:**
- Modify: `register/key.py` (replace PositionKey stub)
- Modify: `tests/test_key.py` (add PositionKey tests)

- [ ] **Step 1: Write tests for PositionKey constructor and validate**

Add to `tests/test_key.py`:

```python
class TestPositionKeyConstructor:
    def test_arity_stored(self):
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        assert k.arity == 2

    def test_arity_defaults_to_zero(self):
        k = PositionKey(1, "xy", "坐标", float)
        assert k.arity == 0

    def test_arity_zero_raises(self):
        from register.exception import RegisterError
        with pytest.raises(RegisterError):
            PositionKey(1, "xy", "坐标", float, arity=0)

    def test_arity_negative_raises(self):
        from register.exception import RegisterError
        with pytest.raises(RegisterError):
            PositionKey(1, "xy", "坐标", float, arity=-1)

    def test_isinstance_register_key(self):
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        assert isinstance(k, RegisterKey)

    def test_eq_same_class_same_id(self):
        k1 = PositionKey(1, "xy", "坐标", float, arity=2)
        k2 = PositionKey(1, "xy", "坐标", float, arity=3)
        assert k1 == k2

    def test_eq_different_class(self):
        p = ParameterKey(1, "x", "X", int)
        pos = PositionKey(1, "x", "X", int, arity=2)
        assert p != pos
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestPositionKeyConstructor -v`
Expected: FAIL — `RegisterError` not raised (stub doesn't validate arity)

- [ ] **Step 3: Implement PositionKey constructor**

Replace the `PositionKey` stub in `register/key.py`:

```python
class PositionKey(_BaseKey):
    """Key for positional values — tuples of the same length."""

    def __init__(
        self, id: int, name: str, name_cn: str, vtype: Any = None, arity: int = 0
    ) -> None:
        super().__init__(id, name, name_cn, vtype)
        if arity < 1:
            raise RegisterError("arity must be >= 1")
        self.arity = arity

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError
```

- [ ] **Step 4: Run constructor tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestPositionKeyConstructor -v`
Expected: All PASS

- [ ] **Step 5: Write tests for PositionKey aggregation**

Add to `tests/test_key.py`:

```python
class TestPositionKeyAggregation:
    def _make_key(self, vtype=float, arity=3):
        return PositionKey(1, "xyz", "坐标", vtype, arity=arity)

    def test_sum_int(self):
        k = self._make_key(int, arity=3)
        result = k.sum(DimensionAsKey(), (1, 2, 3), (4, 5, 6))
        assert result == [5, 7, 9]

    def test_sum_float(self):
        k = self._make_key(float, arity=2)
        result = k.sum(DimensionAsKey(), (1.0, 2.0), (3.0, 4.0))
        assert result == [4.0, 6.0]

    def test_sum_bool(self):
        k = self._make_key(bool, arity=2)
        result = k.sum(DimensionAsKey(), (True, False), (True, True))
        assert result == [2, 1]

    def test_mean_float(self):
        k = self._make_key(float, arity=3)
        result = k.mean(DimensionAsKey(), (1.0, 2.0, 3.0), (3.0, 4.0, 5.0))
        assert result == [2.0, 3.0, 4.0]

    def test_min_int(self):
        k = self._make_key(int, arity=3)
        result = k.min(DimensionAsKey(), (1, 5, 3), (4, 2, 6))
        assert result == [1, 2, 3]

    def test_max_int(self):
        k = self._make_key(int, arity=3)
        result = k.max(DimensionAsKey(), (1, 5, 3), (4, 2, 6))
        assert result == [4, 5, 6]

    def test_range_int(self):
        k = self._make_key(int, arity=3)
        result = k.range(DimensionAsKey(), (1, 5, 3), (4, 2, 6))
        assert result == [3, 3, 3]

    def test_mismatched_lengths_raises(self):
        k = self._make_key(int, arity=3)
        with pytest.raises(ValueError):
            k.sum(DimensionAsKey(), (1, 2, 3), (4, 5))

    def test_empty_args_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int, arity=3)
        with pytest.raises(RegisterError):
            k.sum(DimensionAsKey())

    def test_mean_empty_raises(self):
        from register.exception import RegisterError
        k = self._make_key(float, arity=2)
        with pytest.raises(RegisterError):
            k.mean(DimensionAsKey())

    def test_str_vtype_not_implemented(self):
        k = PositionKey(1, "x", "X", str, arity=2)
        with pytest.raises(NotImplementedError):
            k.sum(DimensionAsKey(), ("a", "b"))
```

- [ ] **Step 6: Run aggregation tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestPositionKeyAggregation -v`
Expected: FAIL — `NotImplementedError`

- [ ] **Step 7: Implement PositionKey aggregation methods**

Replace the remaining stubs in `PositionKey` within `register/key.py`:

```python
    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("sum requires at least one value")
        if self.vtype in (int, float, bool):
            return [sum(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("mean requires at least one value")
        if self.vtype in (int, float, bool):
            return [sum(elems) / len(args) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        if self.vtype in (int, float, bool):
            return [min(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        if self.vtype in (int, float, bool):
            return [max(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        if self.vtype in (int, float, bool):
            return [max(elems) - min(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")
```

- [ ] **Step 8: Run all PositionKey tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -k "PositionKey" -v`
Expected: All PASS

- [ ] **Step 9: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: implement PositionKey with arity and element-wise aggregation"
```

---

### Task 4: IterableKey

**Files:**
- Modify: `register/key.py` (replace IterableKey stub)
- Modify: `tests/test_key.py` (add IterableKey tests)

- [ ] **Step 1: Write tests for IterableKey aggregation**

Add to `tests/test_key.py`:

```python
class TestIterableKeyAggregation:
    def _make_key(self, vtype=int):
        return IterableKey(1, "scores", "分数", vtype)

    # sum
    def test_sum_int(self):
        k = self._make_key(int)
        result = k.sum(DimensionAsKey(), [1, 2, 3], [4, 5])
        assert result == [6, 9]

    def test_sum_float(self):
        k = self._make_key(float)
        result = k.sum(DimensionAsKey(), [1.0, 2.0], [3.0])
        assert result == [3.0, 3.0]

    def test_sum_bool(self):
        k = self._make_key(bool)
        result = k.sum(DimensionAsKey(), [True, False, True], [True])
        assert result == [2, 1]

    def test_sum_int_empty_iterable(self):
        k = self._make_key(int)
        result = k.sum(DimensionAsKey(), [], [1, 2])
        assert result == [0, 3]

    def test_sum_str(self):
        k = self._make_key(str)
        result = k.sum(DimensionAsKey(), ["a", "b", "a"], ["c"])
        assert result == [{"a": 2, "b": 1}, {"c": 1}]

    def test_sum_dimension(self):
        from register.dimension import Dimension
        d1 = Dimension("r1", "区域1", "R1")
        d2 = Dimension("r2", "区域2", "R2")
        k = IterableKey(1, "test", "测试", d1)
        result = k.sum(DimensionAsKey(), [d1, d2, d1], [d2])
        assert result == [{d1: 2, d2: 1}, {d2: 1}]

    def test_sum_empty_args(self):
        k = self._make_key(int)
        result = k.sum(DimensionAsKey())
        assert result == []

    def test_sum_unsupported_vtype(self):
        k = IterableKey(1, "test", "测试", list)
        with pytest.raises(NotImplementedError):
            k.sum(DimensionAsKey(), [[1], [2]])

    # mean
    def test_mean_int(self):
        k = self._make_key(int)
        result = k.mean(DimensionAsKey(), [1, 2, 3], [4, 5])
        assert result == [2.0, 4.5]

    def test_mean_empty_iterable_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.mean(DimensionAsKey(), [])

    def test_mean_str_not_implemented(self):
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.mean(DimensionAsKey(), ["a", "b"])

    # min
    def test_min_int(self):
        k = self._make_key(int)
        result = k.min(DimensionAsKey(), [3, 1, 2], [5, 4])
        assert result == [1, 4]

    def test_min_str(self):
        k = self._make_key(str)
        result = k.min(DimensionAsKey(), ["banana", "apple", "cherry"], ["date", "elderberry"])
        assert result == ["apple", "date"]

    def test_min_empty_iterable_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.min(DimensionAsKey(), [])

    def test_min_dimension_not_implemented(self):
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = IterableKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.min(DimensionAsKey(), [d])

    # max
    def test_max_int(self):
        k = self._make_key(int)
        result = k.max(DimensionAsKey(), [3, 1, 2], [5, 4])
        assert result == [3, 5]

    def test_max_str(self):
        k = self._make_key(str)
        result = k.max(DimensionAsKey(), ["banana", "apple", "cherry"], ["date", "elderberry"])
        assert result == ["cherry", "elderberry"]

    def test_max_empty_iterable_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.max(DimensionAsKey(), [])

    def test_max_dimension_not_implemented(self):
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = IterableKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.max(DimensionAsKey(), [d])

    # range
    def test_range_int(self):
        k = self._make_key(int)
        result = k.range(DimensionAsKey(), [3, 1, 5], [4, 2])
        assert result == [4, 2]

    def test_range_empty_iterable_raises(self):
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.range(DimensionAsKey(), [])

    def test_range_str_not_implemented(self):
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), ["a", "b"])

    def test_range_dimension_not_implemented(self):
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = IterableKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), [d])

    # isinstance
    def test_isinstance_register_key(self):
        k = IterableKey(1, "scores", "分数", int)
        assert isinstance(k, RegisterKey)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py::TestIterableKeyAggregation -v`
Expected: FAIL — `NotImplementedError`

- [ ] **Step 3: Implement IterableKey aggregation methods**

Replace the `IterableKey` stub in `register/key.py`:

```python
class IterableKey(_BaseKey):
    """Key for iterable values — variable-length collections of vtype."""

    def _validate_args(self, args: tuple) -> None:
        for a in args:
            if not a:
                raise RegisterError("iterable must not be empty")

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if self.vtype in (int, float, bool):
            return [sum(a) for a in args]
        elif self.vtype is str or isinstance(self.vtype, Dimension):
            from collections import Counter
            return [dict(Counter(a)) for a in args]
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool):
            return [sum(a) / len(a) for a in args]
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool, str):
            return [min(a) for a in args]
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool, str):
            return [max(a) for a in args]
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool):
            return [max(a) - min(a) for a in args]
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError
```

- [ ] **Step 4: Run all IterableKey tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -k "IterableKey" -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: implement IterableKey with per-iterable reduction aggregation"
```

---

### Task 5: Validate Methods

**Files:**
- Modify: `register/key.py` (implement validate on all three classes)
- Modify: `tests/test_key.py` (add validate tests)

- [ ] **Step 1: Write tests for validate methods**

Add to `tests/test_key.py`:

```python
class TestParameterKeyValidate:
    def test_valid_int_values(self):
        from register.register import DimensionAsKey
        k = ParameterKey(1, "age", "年龄", int)
        dak = DimensionAsKey()
        dak[()][(1,)] = 25
        dak[()][(2,)] = 30
        assert k.validate(dak) is True

    def test_invalid_int_value(self):
        from register.register import DimensionAsKey
        k = ParameterKey(1, "age", "年龄", int)
        dak = DimensionAsKey()
        dak[()][(1,)] = 25
        dak[()][(2,)] = "thirty"
        assert k.validate(dak) is False

    def test_valid_str_values(self):
        from register.register import DimensionAsKey
        k = ParameterKey(1, "code", "编码", str)
        dak = DimensionAsKey()
        dak[()][(1,)] = "A01"
        dak[()][(2,)] = "B02"
        assert k.validate(dak) is True

    def test_valid_dimension_values(self):
        from register.register import DimensionAsKey
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "region", "地区", d)
        dak = DimensionAsKey()
        dak[()][(1,)] = d
        assert k.validate(dak) is True

    def test_invalid_dimension_value(self):
        from register.register import DimensionAsKey
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "region", "地区", d)
        dak = DimensionAsKey()
        dak[()][(1,)] = "not a dimension"
        assert k.validate(dak) is False

    def test_empty_data_is_valid(self):
        from register.register import DimensionAsKey
        k = ParameterKey(1, "age", "年龄", int)
        dak = DimensionAsKey()
        assert k.validate(dak) is True

    def test_none_vtype_is_valid(self):
        from register.register import DimensionAsKey
        k = ParameterKey(1, "x", "X")
        dak = DimensionAsKey()
        dak[()][(1,)] = "anything"
        dak[()][(2,)] = 42
        assert k.validate(dak) is True


class TestPositionKeyValidate:
    def test_valid_tuples(self):
        from register.register import DimensionAsKey
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        dak = DimensionAsKey()
        dak[()][(1,)] = (1.0, 2.0)
        dak[()][(2,)] = (3.0, 4.0)
        assert k.validate(dak) is True

    def test_wrong_arity(self):
        from register.register import DimensionAsKey
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        dak = DimensionAsKey()
        dak[()][(1,)] = (1.0, 2.0, 3.0)
        assert k.validate(dak) is False

    def test_wrong_element_type(self):
        from register.register import DimensionAsKey
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        dak = DimensionAsKey()
        dak[()][(1,)] = (1.0, "not a float")
        assert k.validate(dak) is False

    def test_not_a_tuple(self):
        from register.register import DimensionAsKey
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        dak = DimensionAsKey()
        dak[()][(1,)] = [1.0, 2.0]
        assert k.validate(dak) is False

    def test_empty_data_is_valid(self):
        from register.register import DimensionAsKey
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        dak = DimensionAsKey()
        assert k.validate(dak) is True


class TestIterableKeyValidate:
    def test_valid_lists(self):
        from register.register import DimensionAsKey
        k = IterableKey(1, "scores", "分数", int)
        dak = DimensionAsKey()
        dak[()][(1,)] = [1, 2, 3]
        dak[()][(2,)] = [4, 5]
        assert k.validate(dak) is True

    def test_invalid_element_type(self):
        from register.register import DimensionAsKey
        k = IterableKey(1, "scores", "分数", int)
        dak = DimensionAsKey()
        dak[()][(1,)] = [1, "two", 3]
        assert k.validate(dak) is False

    def test_not_iterable(self):
        from register.register import DimensionAsKey
        k = IterableKey(1, "scores", "分数", int)
        dak = DimensionAsKey()
        dak[()][(1,)] = 42
        assert k.validate(dak) is False

    def test_empty_data_is_valid(self):
        from register.register import DimensionAsKey
        k = IterableKey(1, "scores", "分数", int)
        dak = DimensionAsKey()
        assert k.validate(dak) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -k "Validate" -v`
Expected: FAIL — `NotImplementedError`

- [ ] **Step 3: Implement validate on ParameterKey**

Replace the `validate` stub in `ParameterKey` within `register/key.py`:

```python
    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        if self.vtype is None:
            return True
        for _dim_tuple, idx_dict in data._data.items():
            for _idx_tuple, value in idx_dict.items():
                if not isinstance(value, self.vtype):
                    return False
        return True
```

- [ ] **Step 4: Implement validate on PositionKey**

Replace the `validate` stub in `PositionKey` within `register/key.py`:

```python
    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        if self.vtype is None:
            return True
        for _dim_tuple, idx_dict in data._data.items():
            for _idx_tuple, value in idx_dict.items():
                if not isinstance(value, tuple):
                    return False
                if len(value) != self.arity:
                    return False
                if not all(isinstance(elem, self.vtype) for elem in value):
                    return False
        return True
```

- [ ] **Step 5: Implement validate on IterableKey**

Replace the `validate` stub in `IterableKey` within `register/key.py`:

```python
    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        if self.vtype is None:
            return True
        for _dim_tuple, idx_dict in data._data.items():
            for _idx_tuple, value in idx_dict.items():
                try:
                    elements = iter(value)
                except TypeError:
                    return False
                if not all(isinstance(elem, self.vtype) for elem in elements):
                    return False
        return True
```

- [ ] **Step 6: Run all validate tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -k "Validate" -v`
Expected: All PASS

- [ ] **Step 7: Run all key tests to verify nothing broke**

Run: `cd D:/github/register && python -m pytest tests/test_key.py -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add register/key.py tests/test_key.py
git commit -m "feat: implement validate on ParameterKey, PositionKey, IterableKey"
```

---

### Task 6: Update register.py — Bounded TypeVar, MEAN, Register.validate()

**Files:**
- Modify: `register/register.py`
- Modify: `tests/test_register.py` (create or extend)

- [ ] **Step 1: Write tests for MEAN and Register.validate()**

Create or update `tests/test_register.py`:

```python
import pytest
from register.register import Register, Method, DimensionAsKey
from register.key import RegisterKey, ParameterKey


class TestMethodEnum:
    def test_mean_exists(self):
        assert Method(5) is not None

    def test_mean_repr(self):
        assert repr(Method(5)) == "MEAN"

    def test_mean_equality(self):
        assert Method(5) == Method(5)

    def test_mean_inequality(self):
        assert Method(5) != Method(1)

    def test_all_methods(self):
        names = {repr(Method(i)) for i in range(6)}
        assert names == {"ALL", "SUM", "MAX", "MIN", "RANGE", "MEAN"}


class TestRegisterClassMethods:
    def test_mean_class_attr(self):
        assert Register.MEAN == Method(5)

    def test_all_methods_present(self):
        assert Register.ALL == Method(0)
        assert Register.SUM == Method(1)
        assert Register.MAX == Method(2)
        assert Register.MIN == Method(3)
        assert Register.RANGE == Method(4)
        assert Register.MEAN == Method(5)


class TestRegisterValidate:
    def test_validate_empty_register(self):
        reg = Register()
        assert reg.validate() is True

    def test_validate_valid_data(self):
        reg = Register()
        key = ParameterKey(1, "age", "年龄", int)
        dak = reg[key]
        dak[()][(1,)] = 25
        dak[()][(2,)] = 30
        assert reg.validate() is True

    def test_validate_invalid_data(self):
        reg = Register()
        key = ParameterKey(1, "age", "年龄", int)
        dak = reg[key]
        dak[()][(1,)] = 25
        dak[()][(2,)] = "not an int"
        assert reg.validate() is False

    def test_validate_multiple_keys(self):
        reg = Register()
        k1 = ParameterKey(1, "age", "年龄", int)
        k2 = ParameterKey(2, "name", "名称", str)
        reg[k1][()][(1,)] = 25
        reg[k2][()][(1,)] = "Alice"
        assert reg.validate() is True

    def test_validate_one_key_invalid(self):
        reg = Register()
        k1 = ParameterKey(1, "age", "年龄", int)
        k2 = ParameterKey(2, "name", "名称", str)
        reg[k1][()][(1,)] = 25
        reg[k2][()][(1,)] = 42  # not a str
        assert reg.validate() is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/github/register && python -m pytest tests/test_register.py -v`
Expected: FAIL — `MEAN` not found, `validate` not found

- [ ] **Step 3: Update register.py**

Modify `register/register.py`:

1. Add bounded TypeVar and import RegisterKey:

```python
from .key import RegisterKey

K = TypeVar("K", bound=RegisterKey)
```

2. Add MEAN to Method._NAMES:

```python
class Method(int):
    _NAMES: dict[int, str] = {0: "ALL", 1: "SUM", 2: "MAX", 3: "MIN", 4: "RANGE", 5: "MEAN"}
```

3. Add MEAN class attribute to Register:

```python
class Register(Generic[K]):
    ALL: Method = Method(0)
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    MEAN: Method = Method(5)
```

4. Add `validate` method to Register:

```python
    def validate(self, **config: Any) -> bool:
        rs = True
        for key in self._data:
            data = self._data[key]
            rs &= key.validate(data, **config)
        return rs
```

The complete `register/register.py` after changes:

```python
from __future__ import annotations

import logging
from collections import defaultdict
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


class DimensionAsKey:
    _data: dict[tuple[Any, ...], dict[tuple[int, ...], Any]]

    def __init__(self) -> None:
        self._data = defaultdict(dict)

    def __getitem__(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data[key]

    def __iter__(self) -> Iterator[tuple[Any, ...]]:
        return iter(self._data)

    def __repr__(self) -> str:
        if not self._data:
            return "DimensionAsKey(empty)"
        parts = []
        for dim_tuple, idx_dict in self._data.items():
            dim_names = ",".join(repr(d) for d in dim_tuple)
            parts.append(f"({dim_names}): {len(idx_dict)}")
        return f"DimensionAsKey({{{', '.join(parts)}}})"

    def pop(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data.pop(key, {})


class Register(Generic[K]):
    ALL: Method = Method(0)
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    MEAN: Method = Method(5)
    _data: dict[K, DimensionAsKey]

    def __init__(self) -> None:
        self._data = defaultdict(DimensionAsKey)

    def __getitem__(self, key: K) -> DimensionAsKey:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        if not self._data:
            return "Register(empty)"
        total_cells = 0
        param_summaries = []
        for param, dak in self._data.items():
            cell_count = sum(len(idx_dict) for idx_dict in dak._data.values())
            total_cells += cell_count
            param_summaries.append(f"{param}: {cell_count}")
        return f"Register(params={len(self._data)}, cells={total_cells}, {{{', '.join(param_summaries)}}})"

    def select(
        self,
        key: K,
        dimension: tuple[Dimension, ...],
        target: tuple[int, ...] | None = None,
    ) -> Generator[tuple[int, ...], None, None]:
        for index in self._data[key][dimension]:
            if target is None:
                yield index
            elif all(self.ALL == j or i == j for i, j in zip(index, target)):
                yield index

    def validate(self, **config: Any) -> bool:
        rs = True
        for key in self._data:
            data = self._data[key]
            rs &= key.validate(data, **config)
        return rs


__all__ = [
    "Register",
]
```

- [ ] **Step 4: Run register tests to verify they pass**

Run: `cd D:/github/register && python -m pytest tests/test_register.py -v`
Expected: All PASS

- [ ] **Step 5: Run existing tests to check for regressions**

Run: `cd D:/github/register && python -m pytest tests/ -v`
Expected: Some tests may fail due to `Parameter` being removed — that's expected, we fix in the next task

- [ ] **Step 6: Commit**

```bash
git add register/register.py tests/test_register.py
git commit -m "feat: add MEAN method, bounded TypeVar, and Register.validate()"
```

---

### Task 7: Refactor parameter.py and conftest.py

**Files:**
- Modify: `register/parameter.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Update parameter.py to use ParameterKey**

Replace the contents of `register/parameter.py`:

```python
from .key import ParameterKey

Id = ParameterKey(1, "id", "ID", int)
Code = ParameterKey(2, "code", "编码", str)
Name = ParameterKey(3, "name", "名称", str)


__all__ = [
    "Id",
    "Code",
    "Name",
]
```

- [ ] **Step 2: Update conftest.py**

Replace the contents of `tests/conftest.py`:

```python
import pytest
from register import Register, ParameterKey, Dimension
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
def sample_parameter():
    """Sample ParameterKey for testing."""
    return ParameterKey(100, "test_param", "测试参数", int)


@pytest.fixture
def price_parameter():
    """Price ParameterKey with a float type."""
    return ParameterKey(4, "price", "价格", float)
```

- [ ] **Step 3: Run all tests to verify**

Run: `cd D:/github/register && python -m pytest tests/ -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add register/parameter.py tests/conftest.py
git commit -m "refactor: parameter.py uses ParameterKey, update conftest fixtures"
```

---

### Task 8: Update __init__.py Exports

**Files:**
- Modify: `register/__init__.py`

- [ ] **Step 1: Update __init__.py**

Replace the contents of `register/__init__.py`:

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

- [ ] **Step 2: Run all tests to verify**

Run: `cd D:/github/register && python -m pytest tests/ -v`
Expected: All PASS

- [ ] **Step 3: Verify imports work correctly**

Run:
```bash
cd D:/github/register && python -c "
from register import RegisterKey, ParameterKey, PositionKey, IterableKey
from register import Register, Dimension, Index, Metric
from register import Id, Code, Name
from register import RegisterError, ValidationError, DimensionError

# Verify hierarchy
assert issubclass(ParameterKey, RegisterKey)
assert issubclass(PositionKey, RegisterKey)
assert issubclass(IterableKey, RegisterKey)

# Verify singletons are ParameterKey
assert isinstance(Id, ParameterKey)
assert isinstance(Code, ParameterKey)
assert isinstance(Name, ParameterKey)

# Verify MEAN exists
assert Register.MEAN == 5

print('All imports and assertions verified.')
"
```

- [ ] **Step 4: Commit**

```bash
git add register/__init__.py
git commit -m "feat: update __init__.py exports for new key classes"
```

---

### Task 9: Final Verification

**Files:**
- All modified files

- [ ] **Step 1: Run full test suite**

Run: `cd D:/github/register && python -m pytest tests/ -v --tb=short`
Expected: All tests PASS

- [ ] **Step 2: Run mypy type checking**

Run: `cd D:/github/register && python -m mypy register/`
Expected: No errors (or only pre-existing errors unrelated to this change)

- [ ] **Step 3: Run ruff linting**

Run: `cd D:/github/register && python -m ruff check register/ tests/`
Expected: No errors

- [ ] **Step 4: Verify backward compatibility of sample_register fixture**

Run:
```bash
cd D:/github/register && python -c "
from register import Register, ParameterKey
from register.parameter import Id
from register.dimension import Dimension

# Simulate the sample_register fixture
reg = Register()
region = Dimension('region', '地区', 'REG')
product = Dimension('product', '产品', 'PRD')

reg[Id][(region, product)][(1, 1)] = 1
reg[Id][(region, product)][(1, 2)] = 2
reg[Id][(region, product)][(2, 1)] = 3
reg[Id][(region, product)][(2, 2)] = 4

# Validate
assert reg.validate() is True
print('Backward compatibility verified.')
"
```

- [ ] **Step 5: Final commit (if any cleanup needed)**

```bash
git add -A
git status
# Only commit if there are changes from cleanup
```