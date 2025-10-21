FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install -y git gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-editable --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --no-dev

FROM python:3.13-slim-bookworm AS production

RUN groupadd --system --gid 999 nonroot  \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

ENV PYTHONUNBUFFERED=1 PYTHONOPTIMIZE=2
ENV TZ=Europe/Moscow

COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --from=builder --chown=nonroot:nonroot /app/src /app/src

RUN mkdir -p /app/memory && \
    chown -R nonroot:nonroot /app/memory && \
    chmod -R 777 /app/memory

ENV PATH="/app/.venv/bin:$PATH"

USER nonroot
WORKDIR /app/src
