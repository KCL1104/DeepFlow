# Agent Dockerfile
FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

# Run the agent worker
# Assuming main.py in agent starts the worker process
CMD ["uv", "run", "python", "main.py"]
