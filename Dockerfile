FROM ghcr.io/astral-sh/uv:0.13.6 AS uv

FROM python:3.14-slim

# OpenCV needs these shared libraries even without a display.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    RUFF_CACHE_DIR=/tmp/.ruff_cache \
    PYTEST_ADDOPTS="-p no:cacheprovider"

WORKDIR /app

COPY .python-version pyproject.toml uv.lock ./
RUN uv sync --locked

COPY . .

RUN useradd --create-home app
USER app

CMD ["python", "production_draft.py"]
