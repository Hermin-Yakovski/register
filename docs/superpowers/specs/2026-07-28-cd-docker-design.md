# CD with Docker Design

**Date:** 2026-07-28
**Status:** Approved
**Author:** Design Session

## Overview

Add continuous deployment to the existing CI pipeline. Build a Docker image using the uv official base image and push to GitHub Container Registry (ghcr.io). The CD job runs after CI succeeds, within the same workflow file.

## Architecture

Single `ci.yml` workflow with two jobs: `ci` (existing) and `cd` (new).

| Trigger | CI | CD |
|---------|----|----|
| PR to main | Run | Build image (don't push) |
| Push to main | Run | Build + push `latest` |
| `v*` tag push | Run | Build + push version + `latest` |

**Image registry:** `ghcr.io/<owner>/register`

**Authentication:** Built-in `GITHUB_TOKEN` with `packages: write` permission — no external secrets needed.

## Dockerfile

Single-stage build using uv official base image:

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN uv sync --frozen --no-dev --no-install-workspace

# Copy application code
COPY register/ register/
COPY main.py .

CMD ["uv", "run", "python", "-m", "main"]
```

### Key flags

- `--frozen` — uses exact versions from `uv.lock` for reproducibility
- `--no-dev` — excludes dev dependencies (pytest, ruff, mypy, pytest-cov)
- `--no-install-workspace` — skips installing the package itself in editable mode

### Layer caching strategy

Dependency files (`pyproject.toml`, `uv.lock`) are copied first so the `uv sync` layer is cached when only application code changes.

## GitHub Actions Workflow

Updated `ci.yml` with a `cd` job that depends on `ci`:

```yaml
name: CI/CD

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
    tags: ["v*"]

permissions:
  contents: read
  packages: write

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

  cd:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        if: github.event_name == 'push'
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=raw,value=latest,enable={{is_default_branch}}
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

### Conditional push

- `docker/login-action` only runs on `push` events (not PRs)
- `docker/build-push-action` uses `push: ${{ github.event_name == 'push' }}` — builds on all events, pushes only on push to main or tag

## .dockerignore

```
.git
.venv
.mypy_cache
.pytest_cache
.ruff_cache
.coverage
dist
tests
docs
.idea
```

## Consumption

Images are available as GitHub Packages:

```bash
docker pull ghcr.io/<owner>/register:latest
docker pull ghcr.io/<owner>/register:v0.1.0
docker run ghcr.io/<owner>/register:latest
```

## Verification

Local testing:

```bash
docker build -t register .
docker run register
# Should exit 0
```

## File Changes

| File | Action |
|------|--------|
| `Dockerfile` | Create |
| `.dockerignore` | Create |
| `.github/workflows/ci.yml` | Modify — add `permissions`, add `cd` job |