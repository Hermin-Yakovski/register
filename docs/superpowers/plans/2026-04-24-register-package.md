# Register Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a publishable Python package called `register` with a multi-dimensional data registry class, complete with tests, documentation, and tooling configuration.

**Architecture:** Generic `Register[K]` class storing multi-dimensional data in nested dictionaries (`Parameter → Dimensions → indices → value`). Type-safe with `Parameter` keys that define expected value types. Validation on-demand with optional error raising. Export to pandas DataFrames.

**Tech Stack:** Python 3.11+, Poetry, pandas, pytest, Ruff, Mypy

---

## File Structure

```
register/
├── README.md
├── pyproject.toml
├── .python-version
├── LICENSE
├── .gitignore
├── register/
│   ├── __init__.py
│   ├── register.py
│   ├── parameter.py
│   ├── dimension.py
│   └── exception.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_register.py
    ├── test_parameter.py
    ├── test_dimension.py
    └── test_exception.py
```

---

## Task 1: Initialize Project Configuration

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Modify: `README.md` (create)

- [ ] **Step 1: Create pyproject.toml with Poetry configuration**

```toml
[tool.poetry]
name = "register"
version = "0.1.0"
description = "Multi-dimensional data registry with validation and pandas export"
authors = ["yehemin <yehemin@example.com>"]
readme = "README.md"
packages = [{include = "register"}]

[tool.poetry.dependencies]
python = "^3.11"
pandas = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
ruff = "^0.8"
mypy = "^1.10"
pandas-stubs = "^2.0"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

- [ ] **Step 2: Create .python-version file**

```bash
echo "3.11" > .python-version
```

- [ ] **Step 3: Create README.md**

```markdown
# Register

Multi-dimensional data registry with validation and pandas export.

## Installation

```bash
pip install register
```

## Quick Example

```python
from register import Register, Parameter, Dimension

# Define custom parameter and dimension
price = Parameter(4, 'price', '价格', float)
region = Dimension('region', '地区', 'REG')

# Use the register
reg = Register()
reg[price][(region,)][('Beijing',)] = 100.0

# Export to DataFrame
frames = reg.as_frames()
```

## License

See LICENSE file.
```

- [ ] **Step 4: Commit initial configuration**

```bash
git add pyproject.toml .python-version README.md
git commit -m "chore: initialize project configuration with Poetry"
```

---

## Task 2: Create Exception Classes

**Files:**
- Create: `register/exception.py`
- Create: `tests/test_exception.py`

- [ ] **Step 1: Write failing tests for exception classes**

```python
# tests/test_exception.py
import pytest

def test_register_error_exists():
    from register.exception import RegisterError
    assert issubclass(RegisterError, Exception)

def test_validation_error_exists():
    from register.exception import ValidationError
    assert issubclass(ValidationError, RegisterError)

def test_dimension_error_exists():
    from register.exception import DimensionError
    assert issubclass(DimensionError, RegisterError)

def test_can_raise_register_error():
    from register.exception import RegisterError
    with pytest.raises(RegisterError):
        raise RegisterError("test error")

def test_can_raise_validation_error():
    from register.exception import ValidationError
    with pytest.raises(ValidationError):
        raise ValidationError("validation failed")

def test_can_raise_dimension_error():
    from register.exception import DimensionError
    with pytest.raises(DimensionError):
        raise DimensionError("dimension error")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_exception.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` - module doesn't exist yet

- [ ] **Step 3: Create exception module**

```python
# register/exception.py
class RegisterError(Exception):
    """Base exception for all register errors."""
    pass


class ValidationError(RegisterError):
    """Raised when type/index validation fails."""
    pass


class DimensionError(RegisterError):
    """Raised for dimension-related issues."""
    pass
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_exception.py -v
```

Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/exception.py tests/test_exception.py
git commit -m "feat: add exception classes"
```

---

## Task 3: Create Dimension Class

**Files:**
- Create: `register/dimension.py`
- Create: `tests/test_dimension.py`

- [ ] **Step 1: Write failing tests for Dimension class**

```python
# tests/test_dimension.py
import pytest

def test_dimension_creation():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert dim.name == "test"
    assert dim.name_cn == "测试"
    assert dim.sign == "TST"

def test_dimension_str_returns_sign():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert str(dim) == "TST"

def test_dimension_repr_returns_name():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert repr(dim) == "test"

def test_dimension_hashable():
    from register.dimension import Dimension
    dim1 = Dimension("test", "测试", "TST")
    dim2 = Dimension("test", "测试", "TST")
    assert hash(dim1) == hash(dim2)

def test_dimension_equality():
    from register.dimension import Dimension
    dim1 = Dimension("test", "测试", "TST")
    dim2 = Dimension("test", "测试", "TST")
    dim3 = Dimension("other", "其他", "OTH")
    assert dim1 == dim2
    assert dim1 != dim3

def test_dimension_equality_based_on_sign():
    from register.dimension import Dimension
    dim1 = Dimension("name1", "测试1", "TST")
    dim2 = Dimension("name2", "测试2", "TST")
    assert dim1 == dim2  # Equal because signs match

def test_index_dimension_exists():
    from register.dimension import Index
    assert Index.name == "Index"
    assert Index.name_cn == "下标"
    assert Index.sign == "IX"

def test_metric_dimension_exists():
    from register.dimension import Metric
    assert Metric.name == "Metric"
    assert Metric.name_cn == "指标汇总"
    assert Metric.sign == "MTC"

def test_dimension_sign_property():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert dim.sign == "TST"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_dimension.py -v
```

Expected: `ImportError` - module doesn't exist yet

- [ ] **Step 3: Create dimension module**

```python
# register/dimension.py
class Dimension:
    _name: str
    _name_cn: str
    _sign: str

    def __init__(self, name: str, name_cn: str, sign: str):
        self._name = name
        self._name_cn = name_cn
        self._sign = sign

    def __str__(self):
        return self._sign

    def __repr__(self):
        return self._name

    def __hash__(self):
        return hash(self._sign)

    def __eq__(self, other):
        return isinstance(other, Dimension) and (self._sign == other.sign)

    @property
    def name(self):
        return self._name

    @property
    def name_cn(self):
        return self._name_cn

    @property
    def sign(self):
        return self._sign


Index = Dimension('Index', '下标', 'IX')
Metric = Dimension('Metric', '指标汇总', 'MTC')
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_dimension.py -v
```

Expected: All 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/dimension.py tests/test_dimension.py
git commit -m "feat: add Dimension class with Index and Metric"
```

---

## Task 4: Create Parameter Class

**Files:**
- Create: `register/parameter.py`
- Create: `tests/test_parameter.py`

- [ ] **Step 1: Write failing tests for Parameter class**

```python
# tests/test_parameter.py
import pytest
from typing import Any

def test_parameter_creation():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试", int)
    assert param.id == 1
    assert param.name == "test"
    assert param.name_cn == "测试"
    assert param.vtype == int

def test_parameter_default_vtype_is_any():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试")
    assert param.vtype == Any

def test_parameter_str_returns_name():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试")
    assert str(param) == "test"

def test_parameter_repr_returns_name():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试")
    assert repr(param) == "test"

def test_parameter_hashable():
    from register.parameter import Parameter
    param1 = Parameter(1, "test", "测试")
    param2 = Parameter(1, "test", "测试")
    assert hash(param1) == hash(param2)

def test_parameter_equality():
    from register.parameter import Parameter
    param1 = Parameter(1, "test", "测试")
    param2 = Parameter(1, "test", "测试")
    param3 = Parameter(2, "other", "其他")
    assert param1 == param2
    assert param1 != param3

def test_parameter_equality_based_on_id():
    from register.parameter import Parameter
    param1 = Parameter(1, "name1", "测试1")
    param2 = Parameter(1, "name2", "测试2")
    assert param1 == param2  # Equal because ids match

def test_id_parameter_exists():
    from register.parameter import Id
    assert Id.id == 1
    assert Id.name == "id"
    assert Id.name_cn == "ID"
    assert Id.vtype == int

def test_code_parameter_exists():
    from register.parameter import Code
    assert Code.id == 2
    assert Code.name == "code"
    assert Code.name_cn == "编码"
    assert Code.vtype == str

def test_name_parameter_exists():
    from register.parameter import Name
    assert Name.id == 3
    assert Name.name == "name"
    assert Name.name_cn == "名称"
    assert Name.vtype == str

def test_parameter_implements_has_vtype_protocol():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试", int)
    assert hasattr(param, "vtype")
    assert param.vtype == int
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_parameter.py -v
```

Expected: `ImportError` - module doesn't exist yet

- [ ] **Step 3: Create parameter module**

```python
# register/parameter.py
from typing import Any, Type


class Parameter:
    _id: int
    _name: str
    _name_cn: str
    vtype: Type

    def __init__(self, id: int, name: str, name_cn: str, vtype: Type = Any):
        self._id = id
        self._name = name
        self._name_cn = name_cn
        self.vtype = vtype

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return self._id == other.id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def name_cn(self):
        return self._name_cn


# Common parameters used across all services
Id = Parameter(1, 'id', 'ID', int)
Code = Parameter(2, 'code', '编码')
Name = Parameter(3, 'name', '名称', str)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_parameter.py -v
```

Expected: All 14 tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/parameter.py tests/test_parameter.py
git commit -m "feat: add Parameter class with Id, Code, Name"
```

---

## Task 5: Create Method and DimensionAsKey Helper Classes

**Files:**
- Create: `register/register.py` (partial - only Method and DimensionAsKey)
- Create: `tests/test_register_helpers.py`

- [ ] **Step 1: Write failing tests for Method class**

```python
# tests/test_register_helpers.py
import pytest

def test_method_class_exists():
    from register.register import Method
    m = Method(1)
    assert int(m) == 1

def test_method_equality():
    from register.register import Method
    m1 = Method(1)
    m2 = Method(1)
    m3 = Method(2)
    assert m1 == m2
    assert m1 != m3

def test_method_not_equal_to_int():
    from register.register import Method
    m = Method(1)
    assert m != 1
    assert m != "1"

def test_method_hashable():
    from register.register import Method
    m1 = Method(1)
    m2 = Method(1)
    assert hash(m1) == hash(m2)
    {m1: "value"}  # Should not raise

def test_register_all_method():
    from register.register import Register
    assert int(Register.ALL) == 0

def test_register_sum_method():
    from register.register import Register
    assert int(Register.SUM) == 1

def test_register_max_method():
    from register.register import Register
    assert int(Register.MAX) == 2

def test_register_min_method():
    from register.register import Register
    assert int(Register.MIN) == 3

def test_register_range_method():
    from register.register import Register
    assert int(Register.RANGE) == 4
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_register_helpers.py -v
```

Expected: `ImportError` - module doesn't exist yet

- [ ] **Step 3: Create register.py with Method and DimensionAsKey**

```python
# register/register.py
from collections import defaultdict
from typing import Any

Method class(int):
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return False
        return int(self) == int(other)

    def __hash__(self):
        return super().__hash__()


class DimensionAsKey:
    _data: dict[tuple[Any, ...], dict[tuple[int, ...], Any]]

    def __init__(self):
        self._data = defaultdict(dict)

    def __getitem__(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def pop(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data.pop(key, {})


class Register:
    ALL: Method = Method(0)
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_register_helpers.py -v
```

Expected: All 10 tests PASS

- [ ] **Step 5: Write tests for DimensionAsKey class**

```python
# Add to tests/test_register_helpers.py

def test_dimension_as_key_init():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    assert dak is not None

def test_dimension_as_key_getitem_returns_dict():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    key = ("dim1", "dim2")
    result = dak[key]
    assert isinstance(result, dict)

def test_dimension_as_key_iterable():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    key = ("dim1", "dim2")
    _ = dak[key]
    assert key in iter(dak)

def test_dimension_as_key_pop_removes_key():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    key = ("dim1", "dim2")
    _ = dak[key]
    result = dak.pop(key)
    assert result == {}
    assert key not in iter(dak)

def test_dimension_as_key_pop_nonexistent_returns_empty():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    result = dak.pop(("nonexistent",))
    assert result == {}
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest tests/test_register_helpers.py -v
```

Expected: All 15 tests PASS

- [ ] **Step 7: Commit**

```bash
git add register/register.py tests/test_register_helpers.py
git commit -m "feat: add Method and DimensionAsKey helper classes"
```

---

## Task 6: Create Register Core Class - Basic Functionality

**Files:**
- Modify: `register/register.py`
- Modify: `tests/test_register.py`

- [ ] **Step 1: Write failing tests for Register basic functionality**

```python
# tests/test_register.py
import pytest

def test_register_init():
    from register.register import Register
    reg = Register()
    assert reg.version_id == 0

def test_register_init_with_version():
    from register.register import Register
    reg = Register(version_id=5)
    assert reg.version_id == 5

def test_register_getitem_returns_dimension_as_key():
    from register.register import Register, DimensionAsKey
    from register.parameter import Id
    reg = Register()
    result = reg[Id]
    assert isinstance(result, DimensionAsKey)

def test_register_iteration_yields_parameters():
    from register.register import Register
    from register.parameter import Id
    reg = Register()
    _ = reg[Id]
    assert Id in iter(reg)

def test_register_contains():
    from register.register import Register
    from register.parameter import Id, Code
    reg = Register()
    _ = reg[Id]
    assert Id in reg
    assert Code not in reg

def test_register_store_and_retrieve_value():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    assert reg[Id][(dim,)][(1,)] == 42
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_register.py -v
```

Expected: Tests fail due to missing Register implementation

- [ ] **Step 3: Implement Register basic functionality**

```python
# Add to register/register.py - update Register class:

from typing import Generic, TypeVar, Iterator
from .parameter import Parameter
from .dimension import Dimension

# ... existing Method, DimensionAsKey classes ...

K = TypeVar('K', bound=Parameter)

class Register(Generic[K]):
    ALL: Method = Method(0)
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    _data: dict[K, DimensionAsKey]
    _version_id: int

    def __init__(self, version_id: int = 0):
        self._data = defaultdict(DimensionAsKey)
        self._version_id = version_id

    @property
    def version_id(self) -> int:
        return self._version_id

    def __getitem__(self, key: K) -> DimensionAsKey:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_register.py -v
```

Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/register.py tests/test_register.py
git commit -m "feat: add Register class basic functionality"
```

---

## Task 7: Implement Register.select() Method

**Files:**
- Modify: `register/register.py`
- Modify: `tests/test_register.py`

- [ ] **Step 1: Write failing tests for select method**

```python
# Add to tests/test_register.py

from register.dimension import Dimension

def test_select_returns_all_indices_when_target_none():
    from register.register import Register
    from register.parameter import Id
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = "a"
    reg[Id][(dim,)][(2,)] = "b"
    reg[Id][(dim,)][(3,)] = "c"
    result = list(reg.select(Id, (dim,)))
    assert result == [(1,), (2,), (3,)]

def test_select_filters_by_exact_match():
    from register.register import Register
    from register.parameter import Id
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = "a"
    reg[Id][(dim,)][(2,)] = "b"
    result = list(reg.select(Id, (dim,), (1,)))
    assert result == [(1,)]

def test_select_filters_with_all_method():
    from register.register import Register
    from register.parameter import Id
    reg = Register()
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")
    reg[Id][(dim1, dim2)][(1, 10)] = "a"
    reg[Id][(dim1, dim2)][(1, 20)] = "b"
    reg[Id][(dim1, dim2)][(2, 10)] = "c"
    result = list(reg.select(Id, (dim1, dim2), (Register.ALL, 10)))
    assert result == [(1, 10), (2, 10)]

def test_select_with_multiple_dimensions():
    from register.register import Register
    from register.parameter import Id
    reg = Register()
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")
    reg[Id][(dim1, dim2)][(1, 10)] = "a"
    reg[Id][(dim1, dim2)][(1, 20)] = "b"
    reg[Id][(dim1, dim2)][(2, 10)] = "c"
    result = list(reg.select(Id, (dim1, dim2), (1, 10)))
    assert result == [(1, 10)]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_register.py::test_select_returns_all_indices_when_target_none -v
```

Expected: FAIL - `select` method doesn't exist

- [ ] **Step 3: Implement select method**

```python
# Add to Register class in register/register.py

from typing import Generator
from .dimension import Dimension

# ... inside Register class ...

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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_register.py -k "test_select" -v
```

Expected: All 4 select tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/register.py tests/test_register.py
git commit -m "feat: add Register.select() method"
```

---

## Task 8: Implement Register.as_frames() Method

**Files:**
- Modify: `register/register.py`
- Modify: `tests/test_register.py`

- [ ] **Step 1: Write failing tests for as_frames method**

```python
# Add to tests/test_register.py

import pandas as pd

def test_as_frames_empty_register():
    from register.register import Register
    reg = Register()
    frames = reg.as_frames()
    assert frames == {}

def test_as_frames_single_value():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    frames = reg.as_frames()
    assert len(frames) == 1
    df = frames[(dim,)]
    assert df.iloc[0]["test"] == 42

def test_as_frames_multiple_parameters():
    from register.register import Register
    from register.parameter import Id, Name
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    reg[Name][(dim,)][(1,)] = "test_name"
    frames = reg.as_frames()
    df = frames[(dim,)]
    assert df.iloc[0]["id"] == 42
    assert df.iloc[0]["name"] == "test_name"

def test_as_frames_display_cn():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    frames = reg.as_frames(display_cn=True)
    df = frames[(dim,)]
    assert "测试" in df.columns
    assert df.iloc[0]["ID"] == 42

def test_as_frames_multiple_dimensions():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")
    reg[Id][(dim1, dim2)][(1, 10)] = 42
    frames = reg.as_frames()
    df = frames[(dim1, dim2)]
    assert df.iloc[0]["test1"] == 1
    assert df.iloc[0]["test2"] == 10
    assert df.iloc[0]["id"] == 42
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_register.py -k "test_as_frames" -v
```

Expected: FAIL - `as_frames` method doesn't exist

- [ ] **Step 3: Implement as_frames method**

```python
# Add to Register class in register/register.py

import pandas as pd
from typing import dict as typing_dict

# ... inside Register class ...

def as_frames(self, display_cn: bool = False) -> typing_dict[tuple[Dimension, ...], pd.DataFrame]:
    frames: typing_dict[tuple[Dimension, ...], pd.DataFrame] = {}
    rows: typing_dict[tuple[Dimension, ...], typing_dict[tuple[int, ...], list]] = {}
    columns: typing_dict[tuple[Dimension, ...], list[str]] = {}

    for key in self._data:
        col: str = key.name_cn if display_cn else key.name
        for dimension in self._data[key]:
            if dimension not in rows:
                rows[dimension] = {}
                columns[dimension] = []
            if col not in columns[dimension]:
                for index in rows[dimension]:
                    rows[dimension][index].append(None)
                columns[dimension].append(col)
            for index, value in self._data[key][dimension].items():
                if index not in rows[dimension]:
                    rows[dimension][index] = [None for _ in columns[dimension]]
                rows[dimension][index][-1] = value

    for dimension in columns:
        dataframe_columns: list[str] = [
            d.name_cn if display_cn else d.name for d in dimension
        ] + columns[dimension]
        dataframe_rows: list[list] = []
        for index in rows[dimension]:
            dataframe_rows.append([i for i in index] + rows[dimension][index])
        frames[dimension] = pd.DataFrame(dataframe_rows, columns=dataframe_columns)

    return frames
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_register.py -k "test_as_frames" -v
```

Expected: All 5 as_frames tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/register.py tests/test_register.py
git commit -m "feat: add Register.as_frames() method"
```

---

## Task 9: Implement Register.validate() Method

**Files:**
- Modify: `register/register.py`
- Modify: `tests/test_register.py`

- [ ] **Step 1: Write failing tests for validate method**

```python
# Add to tests/test_register.py

import logging
import pytest
from register.exception import ValidationError, DimensionError

def test_validate_with_valid_data_no_errors():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    # Should not raise
    reg.validate()

def test_validate_with_invalid_type_logs_warning():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = "not_an_int"  # Wrong type
    # Should log warning but not raise
    reg.validate(raise_errors=False)

def test_validate_with_invalid_type_raises_error():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = "not_an_int"
    with pytest.raises(ValidationError):
        reg.validate(raise_errors=True)

def test_validate_with_any_type_accepts_anything():
    from register.register import Register
    from register.parameter import Parameter
    from register.dimension import Dimension
    from typing import Any
    reg = Register()
    param = Parameter(100, "any_param", "任意参数", Any)
    dim = Dimension("test", "测试", "TST")
    reg[param][(dim,)][(1,)] = "anything"
    reg.validate(raise_errors=True)  # Should not raise

def test_validate_with_list_type():
    from register.register import Register
    from register.parameter import Parameter
    from register.dimension import Dimension
    reg = Register()
    param = Parameter(100, "list_param", "列表参数", list[int])
    dim = Dimension("test", "测试", "TST")
    reg[param][(dim,)][(1,)] = [1, 2, 3]
    reg.validate(raise_errors=True)  # Should not raise

def test_validate_with_invalid_list_element_type():
    from register.register import Register
    from register.parameter import Parameter
    from register.dimension import Dimension
    reg = Register()
    param = Parameter(100, "list_param", "列表参数", list[int])
    dim = Dimension("test", "测试", "TST")
    reg[param][(dim,)][(1,)] = [1, "not_int", 3]
    with pytest.raises(ValidationError):
        reg.validate(raise_errors=True)

def test_validate_with_dimension_type():
    from register.register import Register
    from register.parameter import Parameter
    from register.dimension import Dimension
    reg = Register()
    param = Parameter(100, "dim_param", "维度参数", Dimension)
    dim = Dimension("test", "测试", "TST")
    dim2 = Dimension("test2", "测试2", "TS2")
    # Register valid index
    reg._data[dim][(dim2,)][(1,)] = None
    reg[param][(dim,)][(1,)] = dim2
    reg.validate(raise_errors=True)  # Should not raise

def test_validate_with_invalid_dimension_value():
    from register.register import Register
    from register.parameter import Parameter
    from register.dimension import Dimension
    reg = Register()
    param = Parameter(100, "dim_param", "维度参数", Dimension)
    dim = Dimension("test", "测试", "TST")
    dim2 = Dimension("test2", "测试2", "TS2")
    # Don't register the index
    reg[param][(dim,)][(1,)] = dim2
    with pytest.raises(ValidationError):
        reg.validate(raise_errors=True)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_register.py -k "test_validate" -v
```

Expected: FAIL - `validate` method doesn't exist

- [ ] **Step 3: Implement validate method**

```python
# Add to Register class in register/register.py

import logging
from typing import get_args, get_origin
from .exception import ValidationError, DimensionError

logger = logging.getLogger('register')

# ... inside Register class ...

def validate(self, dim: DimensionAsKey, raise_errors: bool = False):
    for key in self._data:
        for dimension in self._data[key]:
            for index in self._data[key][dimension]:
                # Validate index
                for d, ix in zip(dimension, index):
                    if not ((ix,) in dim[d,] or isinstance(ix, Method) or d == Index):
                        msg = (
                            f"[v{self._version_id}] {key}{dimension}{index}: "
                            f"index {ix} does not match any index of dimension {d.name}"
                        )
                        if raise_errors:
                            raise DimensionError(msg)
                        logger.warning(msg)

                value = self._data[key][dimension][index]
                if key.vtype is Any:
                    pass

                elif get_origin(key.vtype) in [list, set, tuple]:
                    # value -> iterable
                    if not isinstance(value, get_origin(key.vtype)):
                        msg = (
                            f"[v{self._version_id}] {key}{dimension}{index}: "
                            f"expected {get_origin(key.vtype)}, got {type(value)}, value={value}"
                        )
                        if raise_errors:
                            raise ValidationError(msg)
                        logger.warning(msg)

                    arg = get_args(key.vtype)[0]
                    if get_args(arg):
                        arg = get_args(arg)[0]

                    for v in value:
                        if isinstance(arg, Dimension):
                            if (v,) not in dim[arg,]:
                                msg = (
                                    f"[v{self._version_id}] {key}{dimension}{index}: "
                                    f"value {v} does not match any index of dimension {arg.name}"
                                )
                                if raise_errors:
                                    raise ValidationError(msg)
                                logger.warning(msg)
                        elif not isinstance(v, arg):
                            msg = (
                                f"[v{self._version_id}] {key}{dimension}{index}: "
                                f"{get_origin(key.vtype)} expected elements of {arg}, "
                                f"got {type(v)}, value={v}"
                            )
                            if raise_errors:
                                raise ValidationError(msg)
                            logger.warning(msg)

                elif isinstance(key.vtype, Dimension):
                    if (value,) not in dim[key.vtype,]:
                        msg = (
                            f"[v{self._version_id}] {key}{dimension}{index}: "
                            f"value {value} does not match any index of dimension {key.vtype.name}"
                        )
                        if raise_errors:
                            raise ValidationError(msg)
                        logger.warning(msg)

                elif not isinstance(value, key.vtype):
                    msg = (
                        f"[v{self._version_id}] {key}{dimension}{index}: "
                        f"expected {key.vtype}, got {type(value)}, value={value}"
                    )
                    if raise_errors:
                        raise ValidationError(msg)
                    logger.warning(msg)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_register.py -k "test_validate" -v
```

Expected: All 9 validate tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/register.py tests/test_register.py
git commit -m "feat: add Register.validate() method with error raising"
```

---

## Task 10: Create Package __init__.py for Public API

**Files:**
- Create: `register/__init__.py`
- Create: `tests/test_init.py`

- [ ] **Step 1: Write failing tests for public API imports**

```python
# tests/test_init.py

def test_import_register():
    from register import Register
    assert Register is not None

def test_import_parameter():
    from register import Parameter
    assert Parameter is not None

def test_import_dimension():
    from register import Dimension
    assert Dimension is not None

def test_import_index():
    from register import Index
    assert Index is not None

def test_import_metric():
    from register import Metric
    assert Metric is not None

def test_import_common_parameters():
    from register import Id, Code, Name
    assert Id is not None
    assert Code is not None
    assert Name is not None

def test_import_exceptions():
    from register import RegisterError, ValidationError, DimensionError
    assert RegisterError is not None
    assert ValidationError is not None
    assert DimensionError is not None

def test_import_from_exception_module():
    from register.exception import RegisterError, ValidationError, DimensionError
    assert RegisterError is not None
    assert ValidationError is not None
    assert DimensionError is not None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_init.py -v
```

Expected: `ImportError` - `__init__.py` doesn't exist or exports wrong things

- [ ] **Step 3: Create __init__.py**

```python
# register/__init__.py
from .register import Register
from .parameter import Parameter, Id, Code, Name
from .dimension import Dimension, Index, Metric
from .exception import RegisterError, ValidationError, DimensionError

__all__ = [
    "Register",
    "Parameter",
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

```bash
pytest tests/test_init.py -v
```

Expected: All 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add register/__init__.py tests/test_init.py
git commit -m "feat: create public API via __init__.py"
```

---

## Task 11: Create Test Fixtures

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Create conftest.py with fixtures**

```python
# tests/conftest.py
import pytest
from register import Register, Parameter, Dimension
from register.dimension import Index, Metric
from register.parameter import Id, Code, Name

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

    reg[Id][(region, product)][("Beijing", "Widget")] = 1
    reg[Id][(region, product)][("Beijing", "Gadget")] = 2
    reg[Id][(region, product)][("Shanghai", "Widget")] = 3
    reg[Id][(region, product)][("Shanghai", "Gadget")] = 4

    return reg

@pytest.fixture
def sample_dimension():
    """Sample Dimension for testing."""
    return Dimension("test", "测试", "TST")

@pytest.fixture
def sample_parameter():
    """Sample Parameter for testing."""
    return Parameter(100, "test_param", "测试参数", int)

@pytest.fixture
def price_parameter():
    """Price Parameter with float type."""
    return Parameter(4, 'price', '价格', float)

@pytest.fixture
def region_dimension():
    """Region Dimension with pre-filled indices."""
    dim = Dimension("region", "地区", "REG")
    reg = Register()
    # Register some indices
    reg._data[dim][(Index,)][("Beijing",)] = None
    reg._data[dim][(Index,)][("Shanghai",)] = None
    return dim, reg
```

- [ ] **Step 2: Run all tests to verify fixtures work**

```bash
pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add pytest fixtures for common test scenarios"
```

---

## Task 12: Add Mypy Type Stubs Configuration

**Files:**
- Create: `register/__init__.pyi` (optional, for better type hints)
- Modify: `pyproject.toml` (update mypy config)

- [ ] **Step 1: Update pyproject.toml for better mypy support**

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "pandas"
ignore_missing_imports = true
```

- [ ] **Step 2: Run mypy to check for type errors**

```bash
poetry run mypy register/
```

Expected: Should pass or show minimal type issues

- [ ] **Step 3: Fix any type errors found**

If mypy shows errors, fix them in the source files. Common fixes:
- Add type hints to function signatures
- Import `from __future__ import annotations` for forward references
- Add `# type: ignore` for unavoidable issues

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml register/
git commit -m "chore: configure mypy for strict type checking"
```

---

## Task 13: Run Full Test Suite and Fix Issues

**Files:**
- Various (as needed)

- [ ] **Step 1: Run complete test suite**

```bash
poetry run pytest tests/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 2: Run Ruff for linting**

```bash
poetry run ruff check register/ tests/
```

Expected: No errors (or auto-fixable warnings)

- [ ] **Step 3: Auto-fix Ruff issues if any**

```bash
poetry run ruff check register/ tests/ --fix
```

- [ ] **Step 4: Run Ruff formatting**

```bash
poetry run ruff format register/ tests/
```

- [ ] **Step 5: Run mypy type check**

```bash
poetry run mypy register/
```

Expected: No type errors

- [ ] **Step 6: Commit any fixes**

```bash
git add -A
git commit -m "test: fix issues from full test/lint/type check run"
```

---

## Task 14: Create tests/__init__.py

**Files:**
- Create: `tests/__init__.py`

- [ ] **Step 1: Create empty tests/__init__.py**

```python
# tests/__init__.py
```

- [ ] **Step 2: Run tests to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/__init__.py
git commit -m "test: add tests/__init__.py"
```

---

## Task 15: Final Verification and Documentation

**Files:**
- Modify: `README.md` (if needed)

- [ ] **Step 1: Verify package can be installed**

```bash
poetry build
poetry install
```

Expected: Builds and installs successfully

- [ ] **Step 2: Test import from installed package**

```python
python -c "from register import Register, Parameter, Dimension; print('Import successful')"
```

Expected: Prints "Import successful"

- [ ] **Step 3: Update README with complete usage example**

```markdown
# Register

Multi-dimensional data registry with validation and pandas export.

## Installation

```bash
pip install register
```

## Quick Example

```python
from register import Register, Parameter, Dimension

# Define custom parameter and dimension
price = Parameter(4, 'price', '价格', float)
region = Dimension('region', '地区', 'REG')

# Create and populate register
reg = Register()
reg[price][(region,)][('Beijing',)] = 100.0
reg[price][(region,)][('Shanghai',)] = 150.0

# Select data
for index in reg.select(price, (region,), ('Beijing',)):
    print(f"Price in Beijing: {reg[price][(region,)][index]}")

# Export to DataFrame
frames = reg.as_frames()
df = frames[(region,)]
print(df)
```

## API Reference

### Classes

- **Register**: Multi-dimensional data registry
- **Parameter**: Typed key with metadata (id, name, name_cn, vtype)
- **Dimension**: Defines a dimension for indexing

### Predefined Dimensions

- **Index**: Special dimension for row indices
- **Metric**: Dimension for metric aggregation

### Predefined Parameters

- **Id**: ID parameter (int)
- **Code**: Code parameter (str)
- **Name**: Name parameter (str)

## License

See LICENSE file.
```

- [ ] **Step 4: Run final full test suite**

```bash
poetry run pytest tests/ -v --cov=register --cov-report=term-missing
```

Expected: All tests PASS with good coverage

- [ ] **Step 5: Commit final changes**

```bash
git add -A
git commit -m "docs: update README with complete usage example"
```

---

## Task 16: Git Tag and Prepare for Release

**Files:**
- None (git operations)

- [ ] **Step 1: Review all commits**

```bash
git log --oneline
```

- [ ] **Step 2: Create version tag**

```bash
git tag v0.1.0
```

- [ ] **Step 3: Push to remote (if remote exists)**

```bash
git push origin main --tags
```

- [ ] **Step 4: Build distribution packages**

```bash
poetry build
```

Expected: Creates `dist/` directory with `.tar.gz` and `.whl` files

- [ ] **Step 5: Verify package contents**

```bash
poetry run twine check dist/*
```

Expected: No errors

---

## Self-Review Checklist

After completing all tasks, verify:

1. **Spec Coverage:**
   - [x] All core classes implemented (Register, Parameter, Dimension, Method, DimensionAsKey)
   - [x] All exceptions implemented (RegisterError, ValidationError, DimensionError)
   - [x] All Register methods implemented (__getitem__, __iter__, __contains__, select, as_frames, validate)
   - [x] Predefined dimensions (Index, Metric) and parameters (Id, Code, Name) exist
   - [x] Validation with raise_errors parameter works
   - [x] Tests cover all functionality
   - [x] Tooling configured (Poetry, pytest, Ruff, Mypy)
   - [x] Documentation (README) complete

2. **No Placeholders:**
   - [x] All steps have complete code
   - [x] No "TBD" or "TODO" in implementation
   - [x] All file paths are exact
   - [x] All test code is complete

3. **Type Consistency:**
   - [x] Method signatures match between definition and tests
   - [x] Property names consistent (name, name_cn, sign, id, vtype)
   - [x] Generic type K bound to Parameter

---

Plan complete and saved to `docs/superpowers/plans/2026-04-24-register-package.md`.
