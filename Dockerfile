FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN uv sync --frozen --no-dev --no-install-workspace

# Copy application code
COPY register/ register/
COPY main.py .
COPY README.md .

CMD ["uv", "run", "python", "-m", "main"]