FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.3 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache \
    XDG_RUNTIME_DIR=/tmp/gunicorn-runtime

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev \
    && DEBUG=True DATABASE_URL= uv run --no-sync python manage.py collectstatic --noinput \
    && groupadd --system django \
    && useradd --system --gid django --home-dir /app django \
    && mkdir -p /app/media "${UV_CACHE_DIR}" "${XDG_RUNTIME_DIR}" \
    && chown -R django:django /app/media "${UV_CACHE_DIR}" "${XDG_RUNTIME_DIR}" \
    && chmod 0700 "${XDG_RUNTIME_DIR}"

USER django

EXPOSE 8000

CMD ["sh", "-c", "uv run --no-sync python manage.py migrate --noinput && exec uv run --no-sync gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3}"]
