# Use a slim Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the project files needed for installing dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync (frozen lockfile, excluding dev dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Final image stage
FROM python:3.13-slim-bookworm

WORKDIR /app

# Copy the application code
COPY . .

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables to run python from the virtualenv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the API port
EXPOSE 8000

# Command to run migrations and start the application
#CMD ["sh", "-c", "alembic upgrade head && python start.py"]
CMD ["sh", "-c", "python start.py"]
