FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PORT=8000

WORKDIR /app

RUN pip install --no-cache-dir uv

# Install dependencies first for better layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy source and install the local project package.
COPY src ./src
COPY main.py ./main.py
RUN uv sync --frozen --no-dev

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn deepflow_backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
