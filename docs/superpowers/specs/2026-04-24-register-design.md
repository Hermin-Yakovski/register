# Register Package Design

**Date:** 2026-04-24
**Status:** Approved
**Author:** Design Session

## Overview

A multi-dimensional data registry for storing, querying, validating, and exporting indexed data with dimension-aware type checking. The package will be published to PyPI as `register`, allowing users to install via `pip install register` and import via `from register import Register`.

## Package Structure

```
register/
├── README.md                    # Package documentation
├── pyproject.toml               # Poetry config + tool settings
├── LICENSE                      # License file (already exists)
├── .gitignore                   # Git ignore (already exists)
├── .python-version              # Python 3.11 (for pyenv/uv users)
│
├── register/                    # Package directory
│   ├── __init__.py              # Public API exports
│   ├── register.py              # Core Register class
│   ├── parameter.py             # Parameter class
│   ├── dimension.py             # Dimension class + Index, Metric
│   └── exception.py             # Custom exceptions
│
└── tests/                       # Test suite
    ├── __init__.py
    ├── conftest.py              # Pytest fixtures
    ├── test_register.py
    ├── test_parameter.py
    ├── test_dimension.py
    └── test_exception.py
```

## Architecture & Components

### Core Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `Register` | register.py | Multi-dimensional data storage, selection, validation, DataFrame export |
| `Parameter` | parameter.py | Typed key with id, name, name_cn, vtype metadata |
| `Dimension` | dimension.py | Defines a dimension with name, name_cn, sign for indexing |
| `DimensionAsKey` | register.py | Internal helper for dimension-indexed lookups |
| `Method` | register.py | Enum-like class for aggregation methods (ALL, SUM, MAX, MIN, RANGE) |

### Custom Exceptions

| Exception | Purpose |
|-----------|---------|
| `RegisterError` | Base exception for all register errors |
| `ValidationError` | Raised when type/index validation fails |
| `DimensionError` | Raised for dimension-related issues (e.g., dimension mismatch) |

### Data Storage Model

Data is stored as nested dictionaries:
```
_data[Parameter][(Dimension1, Dimension2, ...)][(idx1, idx2, ...)] = value
```

### Public API

The package exports via `__init__.py`:
```python
from register import Register, Parameter, Dimension
from register import Index, Metric  # Predefined dimensions
from register.exception import RegisterError, ValidationError, DimensionError
```

## Key Functionality

### Register Class Methods

| Method | Purpose |
|--------|---------|
| `__getitem__(key)` | Access `DimensionAsKey` for a parameter |
| `select(key, dimension, target=None)` | Generator yielding matching indices |
| `as_frames(display_cn=False)` | Export all data as dict of DataFrames |
| `validate(raise_errors=False)` | Validate all stored data against dimension/vtype |

### Predefined Dimensions

- `Index` - Special dimension for row indices (sign: 'IX')
- `Metric` - Dimension for metric aggregation (sign: 'MTC')

### Predefined Parameters

- `Id` - ID parameter (int type)
- `Code` - Code parameter (str type)
- `Name` - Name parameter (str type)

### Validation Behavior

The `validate()` method accepts a `raise_errors: bool = False` parameter:
- When `False`: logs warnings only (current behavior, backward compatible)
- When `True`: raises `ValidationError` or `DimensionError` on issues

## Configuration

### Dependencies

**Runtime:**
- Python >=3.11
- pandas ^2.0

**Development:**
- pytest ^8.0
- ruff ^0.8
- mypy ^1.10
- pandas-stubs ^2.0

### Tool Configuration

**Ruff:**
- Line length: 100
- Target version: Python 3.11

**Mypy:**
- Python version: 3.11
- Mode: strict

## Testing

### Test Structure

Tests are organized by module:
- `test_register.py` - Register class tests
- `test_parameter.py` - Parameter class tests
- `test_dimension.py` - Dimension class tests
- `test_exception.py` - Exception tests
- `conftest.py` - Pytest fixtures

### Test Coverage

| Category | Coverage |
|----------|----------|
| Unit tests | Each class method in isolation |
| Integration tests | Full workflows (insert → select → validate → export) |
| Edge cases | Empty registers, None values, Method comparisons |
| Type validation | Correct/incorrect vtype handling |
| Dimension validation | Valid/invalid index handling |

## Publishing

Version management via `pyproject.toml` using Poetry. Publish with:
```bash
poetry build
poetry publish
```
