FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    llama-cpp-python==0.2.90 \
    flask==3.0.0 \
    gunicorn==21.2.0 \
    huggingface-hub==0.20.0

COPY app.py /app/app.py
COPY server.py /app/server.py

RUN mkdir -p /app/models

ENV MODEL_REPO=TheBloke/deepseek-coder-1.3b-instruct-GGUF
ENV MODEL_FILE=deepseek-coder-1.3b-instruct-q4_k_m.gguf
ENV MODEL_PATH=/app/models/model.gguf
ENV PORT=7860
ENV HOST=0.0.0.0

EXPOSE 7860

CMD ["python", "app.py"]
