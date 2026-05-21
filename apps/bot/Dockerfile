FROM python:3.13-slim AS builder

WORKDIR /build

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (production only)
RUN uv sync --frozen --no-dev --no-cache

# Copy source code
COPY src/ ./src/

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src

# Use venv Python
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot
CMD ["python", "-m", "src"]
