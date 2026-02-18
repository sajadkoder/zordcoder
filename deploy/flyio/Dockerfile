ARG USE_GPU=false
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

FROM base AS cpu-base

RUN echo "Building CPU-only image"

FROM base AS gpu-base

RUN echo "Building GPU-enabled image"

FROM cpu-base AS cpu-final
COPY requirements-cpu.txt requirements.txt

FROM gpu-base AS gpu-final
COPY requirements-gpu.txt requirements.txt

FROM ${USE_GPU:false} AS final

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/models && chmod 777 /data/models

ENV MODEL_CACHE_DIR=/data/models
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "main.py"]
