# uv Migration Design

**Date:** 2026-07-28  
**Status:** Draft  
**Scope:** Replace Poetry with uv for dependency management, building, and CI

## Overview

Migrate the `register` project from Poetry to uv. This is a full replacement — uv handles dependency installation, lock file management, building, and CI. No hybrid approach.

## Goals

- Remove all Poetry dependencies (poetry-core, poetry.lock)
- Use uv for local development and CI
- Maintain the same build artifacts (sdist and wheel)
- Keep CI behavior identical (lint, format check, type check, test, build)

## Non-Goals

- Adding PyPI publishing (keep manual for now)
- Changing the package structure or code
- Modifying tests or documentation beyond what's necessary

## Decisions

### Build Backend: hatchling

**Choice:** hatchling  
**Alternatives considered:**
- poetry-core (keep current) — works with uv but leaves Poetry as a build dependency
- setuptools — more verbose, heavier for a pure-Python package

**Rationale:** hatchling is the modern PEP 621-native backend that pairs naturally with uv. It's fast, minimal, and handles pure-Python packages with type markers cleanly.

### Lock File: Start Fresh

**Choice:** Delete poetry.lock, generate uv.lock from scratch  
**Alternative:** Convert poetry.lock using `uv lock --from-poetry`

**Rationale:** The dependency set is small (4 dev deps, 0 runtime deps), so fresh resolution is low-risk and produces a clean uv.lock without legacy resolution artifacts.

### Dependency Groups: PEP 735

**Choice:** Use `[dependency-groups]` for dev dependencies  
**Alternative:** Use `[project.optional-dependencies]`

**Rationale:** PEP 735 dependency groups are uv's native way to organize non-production dependencies. They're clearer than optional-dependencies (which imply "extras" that users might install) and separate from the published package metadata.

### Python Version Management: uv-native

**Choice:** Let uv manage Python via `.python-version`  
**Alternative:** Keep setup-python in CI

**Rationale:** uv reads `.python-version` natively and can install/manage Python versions automatically. This simplifies CI (no setup-python step) and ensures local and CI environments match.

## Implementation

### 1. pyproject.toml

Replace Poetry-specific configuration with PEP 621 + hatchling:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "register"
version = "0.1.0"
description = "Multi-dimensional data registry"
authors = [{name = "yehemin", email = "yehemin@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
    "mypy>=1.10",
    "pytest-cov>=7.1.0",
]

[tool.hatch.build.targets.wheel]
packages = ["register"]
```

**Key changes:**
- Build backend: `poetry-core` → `hatchling`
- Metadata: `[tool.poetry]` → `[project]` (PEP 621)
- Python version: `^3.11` → `>=3.11`
- Dev deps: `[tool.poetry.group.dev.dependencies]` → `[dependency-groups]`
- Build config: Explicit `packages` for hatchling (py.typed is included automatically)

### 2. CI Pipeline (.github/workflows/ci.yml)

Replace Poetry steps with uv:

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    tags: ["v*"]

jobs:
  ci:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync

      - name: Lint
        run: uv run ruff check

      - name: Format check
        run: uv run ruff format --check

      - name: Type check
        run: uv run mypy register/

      - name: Test
        run: uv run pytest --cov --cov-report=term-missing

      - name: Build
        run: uv build

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        if: success()
        with:
          name: register-dist
          path: dist/
          retention-days: 7
```

**Key changes:**
- Remove `setup-python` (uv manages Python)
- Replace `pip install poetry` with `astral-sh/setup-uv@v6`
- Replace `poetry install` with `uv sync`
- Replace `poetry run` with `uv run`
- Replace `poetry build` with `uv build`
- Remove `cache: "poetry"` (uv has built-in caching)

### 3. Local Workflow

**Command mapping:**

| Task | Poetry | uv |
|---|---|---|
| Install deps | `poetry install` | `uv sync` |
| Add runtime dep | `poetry add foo` | `uv add foo` |
| Add dev dep | `poetry add --group dev foo` | `uv add --group dev foo` |
| Remove dep | `poetry remove foo` | `uv remove foo` |
| Run command | `poetry run pytest` | `uv run pytest` |
| Build dist | `poetry build` | `uv build` |
| Update lock | `poetry update` | `uv lock --upgrade` |

### 4. Migration Steps

1. Rewrite `pyproject.toml` with hatchling + PEP 621 configuration
2. Rewrite `.github/workflows/ci.yml` with uv-based steps
3. Delete `poetry.lock`
4. Run `uv lock` to generate `uv.lock`
5. Run `uv sync` to verify installation
6. Run `uv run pytest` to verify tests pass
7. Commit the changes

### 5. Unchanged Files

- `.python-version` — uv reads it natively
- `register/` — package code untouched
- `tests/` — test code untouched
- `docs/` — documentation untouched
- `README.md` — end-user install instructions (`pip install register`) remain valid

## Verification

After migration, verify:

1. `uv sync` installs all dependencies without errors
2. `uv run pytest --cov --cov-report=term-missing` passes with same coverage
3. `uv run ruff check` passes
4. `uv run ruff format --check` passes
5. `uv run mypy register/` passes
6. `uv build` produces `dist/register-0.1.0.tar.gz` and `dist/register-0.1.0-py3-none-any.whl`
7. CI pipeline runs successfully on the PR

## Risks

**Low risk:** The dependency set is small and standard. All tools (pytest, ruff, mypy) work identically under uv.

**Mitigation:** Run full test suite and build verification before committing. CI will catch any issues on the PR.
