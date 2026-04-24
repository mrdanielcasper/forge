# Stage 1: Builder using 'uv'
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Production Image
FROM python:3.11-slim-bookworm
WORKDIR /app
# Copy the environment from the builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv
# Put the virtual environment on the path
ENV PATH="/app/.venv/bin:$PATH"
# Copy the actual API code
COPY ./src/api /app/src/api

# TODO: Ensure your FastAPI application instance is located at src/api/main.py
# If it is located elsewhere, update the uvicorn target below.
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]