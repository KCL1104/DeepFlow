# Use Python slim image without additional apt packages
FROM python:3.13-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app/src

# Run the agent
CMD ["uv", "run", "python", "main.py"]
