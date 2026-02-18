#!/bin/bash
set -e

echo "=========================================="
echo "  Zord Coder - Build Script"
echo "=========================================="

echo "[1/3] Installing dependencies..."
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir gunicorn

echo "[2/3] Verifying installation..."
python -c "import llama_cpp; print('llama-cpp-python:', llama_cpp.__version__)"

echo "[3/3] Preparing directories..."
mkdir -p /app/models

echo "=========================================="
echo "  Build complete!"
echo "=========================================="
