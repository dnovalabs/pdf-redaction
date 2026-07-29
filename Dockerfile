# syntax=docker/dockerfile:1.9
# PDF Redactor — FastAPI app served by uvicorn.

# ---------- builder ----------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies only: this layer is cached until uv.lock or pyproject.toml change.
# --no-install-project: the app has no build backend and is run by module path,
# so we install its dependencies but never build the project itself.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app

# ---------- runtime ----------
FROM python:3.12-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

# Own the dir itself (COPY --chown only covers contents) so the non-root app user
# can write the materialized secret files at startup, and make the entrypoint exec.
RUN chown app:app /app && chmod +x /app/docker-entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

EXPOSE 8000

# Entrypoint writes the Infisical-injected file secrets, then execs the CMD.
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# One worker per container — scale with replicas, not --workers.
# uvicorn adds the working directory to sys.path, so `app:app` resolves app.py.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
