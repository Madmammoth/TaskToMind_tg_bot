FROM python:3.13-slim-bullseye AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/.venv/bin:$PATH"
WORKDIR /build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/.venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /build/.venv /.venv
COPY docker-entrypoint.sh main.py alembic.ini ./
COPY app ./app/
CMD ["./docker-entrypoint.sh"]