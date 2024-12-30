FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ARG VARIANT=cpu

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VARIANT=$VARIANT

WORKDIR /app
COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --link-mode=copy --extra $VARIANT