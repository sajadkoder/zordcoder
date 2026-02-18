#!/bin/bash
set -e

echo "=========================================="
echo "  Zord Coder - Starting Server"
echo "=========================================="

MODEL_PATH="${ZORD_MODEL_PATH:-/app/models/zordcoder-v1-q4_k_m.gguf}"
N_CTX="${ZORD_N_CTX:-2048}"
N_THREADS="${ZORD_N_THREADS:-2}"
PORT="${PORT:-10000}"
HOST="0.0.0.0"

if [ ! -f "$MODEL_PATH" ]; then
    echo "[STARTUP] Model not found, downloading..."
    python scripts/download_model.py
fi

if [ -f "$MODEL_PATH" ]; then
    SIZE_MB=$(du -m "$MODEL_PATH" | cut -f1)
    echo "[STARTUP] Model ready: $MODEL_PATH (${SIZE_MB} MB)"
else
    echo "[STARTUP] WARNING: Model download failed, starting in demo mode"
fi

echo "[STARTUP] Configuration:"
echo "  - Host: $HOST:$PORT"
echo "  - Context: $N_CTX"
echo "  - Threads: $N_THREADS"
echo "  - Model: $MODEL_PATH"

echo "[STARTUP] Starting server..."
cd /app
exec python web/server.py \
    --host "$HOST" \
    --port "$PORT" \
    --model "$MODEL_PATH" \
    --ctx "$N_CTX" \
    --threads "$N_THREADS"
