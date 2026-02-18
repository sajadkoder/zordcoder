#!/bin/bash

echo "========================================"
echo "   Local Hosting with Tunnel"
echo "========================================"
echo

PORT=8000
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"

PYTHON_EXE=""

if command -v python3 &> /dev/null; then
    if python3 -c "import llama_cpp" 2>/dev/null; then
        PYTHON_EXE="python3"
        echo "Found Python with llama-cpp-python"
    fi
fi

if [ -z "$PYTHON_EXE" ] && command -v python &> /dev/null; then
    if python -c "import llama_cpp" 2>/dev/null; then
        PYTHON_EXE="python"
        echo "Found Python with llama-cpp-python"
    fi
fi

if [ -z "$PYTHON_EXE" ]; then
    echo
    echo "ERROR: Could not find Python with llama-cpp-python installed."
    echo
    echo "Please install it with one of these methods:"
    echo
    echo "  Method 1 - Using pip:"
    echo "    pip install llama-cpp-python"
    echo
    echo "  Method 2 - Using conda:"
    echo "    conda install -c conda-forge llama-cpp-python"
    echo
    exit 1
fi

echo "Using Python: $PYTHON_EXE"
echo

echo "[1/2] Starting server on port $PORT..."
echo

$PYTHON_EXE web/server.py --port $PORT &
PYTHON_PID=$!

sleep 3

echo
echo "[2/2] Choose tunnel option:"
echo
echo "  1. ngrok"
echo "  2. Cloudflare Tunnel (cloudflared)"
echo "  3. Tailscale serve"
echo "  4. Skip tunnel (local only)"
echo "  5. Exit"
echo

read -p "Enter your choice (1-5): " choice

cleanup() {
    echo
    echo "Stopping server..."
    kill $PYTHON_PID 2>/dev/null
    echo "Done."
    exit 0
}

trap cleanup SIGINT SIGTERM

case $choice in
    1)
        echo
        echo "Starting ngrok tunnel..."
        echo
        ngrok http $PORT
        ;;
    2)
        echo
        echo "Starting Cloudflare Tunnel..."
        echo
        cloudflared tunnel --url http://localhost:$PORT
        ;;
    3)
        echo
        echo "Starting Tailscale serve..."
        echo
        echo "Make sure Tailscale is running and you're authenticated."
        echo
        tailscale serve --bg --https=:443 http://localhost:$PORT
        echo
        echo "Your Tailscale URL: https://$(tailscale ip -4)"
        echo
        read -p "Press Enter to stop..."
        tailscale serve --reset
        ;;
    4)
        echo
        echo "========================================"
        echo "Local server running at:"
        echo "  http://localhost:$PORT"
        echo "========================================"
        echo
        read -p "Press Enter to stop..."
        ;;
    5)
        ;;
esac

cleanup
