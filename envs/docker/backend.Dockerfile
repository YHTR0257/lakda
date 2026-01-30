# ======================
# Multi-stage Dockerfile for Backend
# ======================
FROM python:3.12-slim AS development

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen

COPY backend/src ./src

ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# 開発時はホットリロード有効
CMD ["uvicorn", "lakda.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =====================
# Production Stage
# =====================
FROM python:3.12-slim AS production

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/src ./src

ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "lakda.main:app", "--host", "0.0.0.0", "--port", "8000"]