FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY web/ ./web/
COPY scripts/ ./scripts/
COPY deploy/render/start.sh ./start.sh

RUN chmod +x start.sh

RUN mkdir -p /app/models

RUN python scripts/download_model.py || echo "Model will be downloaded at runtime"

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

CMD ["./start.sh"]
