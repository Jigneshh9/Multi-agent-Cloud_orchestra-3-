# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime deps (optional extras are layered in the full image).
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install -e ".[api,postgres,vector,rl,otel]"

# Non-root user for production.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/chroma_data /app/models \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default entrypoint: the FastAPI control plane. Override for dedicated agents.
ENTRYPOINT ["cloud-orchestra"]
CMD ["api"]
