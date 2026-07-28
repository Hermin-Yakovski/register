# uv Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Poetry with uv for dependency management, building, and CI

**Architecture:** Rewrite pyproject.toml to use hatchling build backend with PEP 621 metadata. Update CI to use uv instead of Poetry. Generate fresh uv.lock file.

**Tech Stack:** uv, hatchling, PEP 621, PEP 735

---

### Task 1: Rewrite pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Replace entire pyproject.toml content**

Replace the entire file with this PEP 621 + hatchling configuration:

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

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
exclude = ["tests/"]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
```

- [ ] **Step 2: Commit the change**

```bash
git add pyproject.toml
git commit -m "build: migrate from poetry to hatchling + PEP 621"
```

---

### Task 2: Rewrite CI Workflow

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Replace entire CI workflow**

Replace the entire file with this uv-based workflow:

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

- [ ] **Step 2: Commit the change**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: migrate from poetry to uv"
```

---

### Task 3: Generate uv.lock

**Files:**
- Delete: `poetry.lock`
- Create: `uv.lock`

- [ ] **Step 1: Delete poetry.lock**

```bash
git rm poetry.lock
```

- [ ] **Step 2: Generate uv.lock**

```bash
uv lock
```

Expected: Creates `uv.lock` file with resolved dependencies

- [ ] **Step 3: Verify uv.lock was created**

```bash
ls -la uv.lock
```

Expected: File exists and is non-empty

- [ ] **Step 4: Commit the change**

```bash
git add uv.lock
git commit -m "build: replace poetry.lock with uv.lock"
```

---

### Task 4: Verify Local Workflow

**Files:**
- None (verification only)

- [ ] **Step 1: Install dependencies**

```bash
uv sync
```

Expected: All dependencies install without errors

- [ ] **Step 2: Run tests**

```bash
uv run pytest --cov --cov-report=term-missing
```

Expected: All tests pass with coverage report

- [ ] **Step 3: Run linter**

```bash
uv run ruff check
```

Expected: No linting errors

- [ ] **Step 4: Run format check**

```bash
uv run ruff format --check
```

Expected: All files properly formatted

- [ ] **Step 5: Run type checker**

```bash
uv run mypy register/
```

Expected: No type errors

- [ ] **Step 6: Commit any formatting fixes (if needed)**

If any checks failed and you fixed them:

```bash
git add -u
git commit -m "fix: resolve linting/formatting issues"
```

---

### Task 5: Verify Build

**Files:**
- None (verification only)

- [ ] **Step 1: Build the package**

```bash
uv build
```

Expected: Creates `dist/register-0.1.0.tar.gz` and `dist/register-0.1.0-py3-none-any.whl`

- [ ] **Step 2: Verify build artifacts**

```bash
ls -la dist/
```

Expected output should include:
```
register-0.1.0-py3-none-any.whl
register-0.1.0.tar.gz
```

- [ ] **Step 3: Inspect wheel contents**

```bash
unzip -l dist/register-0.1.0-py3-none-any.whl | head -20
```

Expected: Should include `register/__init__.py`, `register/py.typed`, and other package files

- [ ] **Step 4: Clean up build artifacts**

```bash
rm -rf dist/
```

---

### Task 6: Final Verification

**Files:**
- None (verification only)

- [ ] **Step 1: Check git status**

```bash
git status
```

Expected: Clean working tree, all changes committed

- [ ] **Step 2: Review commit history**

```bash
git log --oneline -5
```

Expected: Recent commits for the migration

- [ ] **Step 3: Push and verify CI**

```bash
git push origin uv
```

Expected: CI pipeline runs successfully on GitHub

---

## Summary

This plan migrates the project from Poetry to uv in 6 focused tasks:

1. **Rewrite pyproject.toml** - Switch to hatchling + PEP 621
2. **Rewrite CI workflow** - Use uv instead of Poetry
3. **Generate uv.lock** - Replace poetry.lock with fresh resolution
4. **Verify local workflow** - Ensure all tools work under uv
5. **Verify build** - Confirm artifacts are correct
6. **Final verification** - Push and confirm CI passes

Each task is self-contained and verifiable. The migration is complete when CI passes on the PR.
