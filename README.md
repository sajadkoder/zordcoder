# Zord Coder v1

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Platform-Termux-orange" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.9+-yellow" alt="Python">
</p>

> **Zord Coder v1** - A multilingual coding assistant optimized for Android Termux. Built with model merging techniques, nanoGPT philosophy, and GGUF inference for fast performance on mobile devices.

---

## Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Interfaces](#interfaces)
  - [CLI (Command Line Interface)](#cli-command-line-interface)
  - [Next.js Web Interface](#nextjs-web-interface)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Fast Inference** - Optimized GGUF quantization for mobile devices
- **Web Interface** - Modern Next.js web UI with dark/light themes
- **CLI Interface** - Terminal interface with syntax highlighting
- **Multi-Language Support** - Python, JavaScript, TypeScript, C++, Rust, Go, Java, Bash, and more
- **Interactive Chat** - Chat interface with code highlighting
- **Streaming Responses** - Real-time token generation
- **Reasoning Mode** - Chain-of-thought reasoning for complex problems
- **Termux Ready** - Optimized for Android devices
- **Usage Tracking** - Built-in daily usage limits (50 messages, 50K tokens)

---

## System Requirements

### Minimum
- Android 7.0+ / Windows 10 / Linux
- 3GB RAM
- 2GB Storage
- Python 3.9+

### Recommended
- Android 10+ / Windows 11 / Linux
- 6GB+ RAM
- 4GB+ Storage
- Python 3.11+

---

## Installation

### Prerequisites

Ensure you have the following installed:
- Python 3.9 or higher with llama-cpp-python
- pip (Python package manager)
- Git (for cloning the repository)
- Node.js 18+ and npm (for web interface)

### Quick Install (Windows with Miniconda)

The easiest way to set up on Windows is using Miniconda, which provides pre-built packages:

1. **Install Miniconda** from https://docs.conda.io/en/latest/miniconda.html

2. **Clone and Setup:**
```powershell
# Clone the repository
git clone https://github.com/sajadkoder/zordcoder.git
cd zordcoder

# Activate conda base environment
conda activate base

# Install dependencies
pip install llama-cpp-python rich huggingface-hub
```

3. **Run:**
```powershell
# Use the provided batch files
.\start_server.bat    # Start the web API server
.\run_cli.bat         # Run the CLI interface
```

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/sajadkoder/zordcoder.git
cd zordcoder

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac/Termux:
source venv/bin/activate

# Install core dependencies
pip install llama-cpp-python rich huggingface-hub

# Install additional dependencies (optional)
pip install -r requirements.txt
```

**Note for Windows users:** Installing `llama-cpp-python` requires compilation. If the install fails:
1. Use Miniconda (recommended): `conda install -c conda-forge llama-cpp-python`
2. Or use a pre-built wheel from: https://github.com/abetlen/llama-cpp-python/releases

### Termux Installation (Android)

```bash
# Update packages
pkg update && pkg upgrade

# Install Python and Git
pkg install python git

# Clone repository
git clone https://github.com/sajadkoder/zordcoder.git
cd zordcoder

# Install dependencies
pip install llama-cpp-python rich huggingface-hub
```

Alternatively, use the provided setup script:

```bash
bash scripts/setup_termux.sh
```

---

## Quick Start

### Option 1: CLI (Fastest)

**Windows (with Miniconda):**
```powershell
cd zordcoder
.\run_cli.bat --interactive
```

**Linux/Mac:**
```bash
cd zordcoder
python scripts/zord_cli.py --interactive
```

The model will download automatically on first run (~833MB from HuggingFace).

### Option 2: Web Interface

**Windows (with Miniconda):**
```powershell
# Terminal 1: Start the Python backend server
cd zordcoder
.\start_server.bat

# Terminal 2: Start the Next.js frontend
cd zordcoder\web
npm install
npm run dev
```

**Linux/Mac:**
```bash
# Terminal 1: Start the Python backend server
cd zordcoder
python web/server.py

# Terminal 2: Start the Next.js frontend
cd zordcoder/web
npm install
npm run dev
```

Visit: http://localhost:3000

---

## Interfaces

### CLI (Command Line Interface)

The CLI provides a terminal-based interface with syntax highlighting and streaming responses.

#### Starting the CLI

**Windows:**
```powershell
.\run_cli.bat --interactive
```

**Linux/Mac:**
```bash
# Interactive mode (recommended)
python scripts/zord_cli.py --interactive

# Single prompt mode
python scripts/zord_cli.py "Write a Python function to calculate factorial"

# With custom settings
python scripts/zord_cli.py "Explain recursion" \
    --temperature 0.2 \
    --max-tokens 512 \
    --context 2048
```

#### CLI Commands

| Command | Description |
|---------|-------------|
| `clear` | Clear conversation history |
| `reasoning` | Toggle reasoning mode (chain-of-thought) |
| `stream` | Toggle streaming mode |
| `metrics` | Show performance metrics |
| `history` | Show conversation history |
| `language <lang>` | Set preferred programming language |
| `temp <value>` | Set temperature (0.0-1.0) |
| `max <tokens>` | Set max tokens to generate |
| `info` | Show model information |
| `help` | Show help message |
| `exit` | Exit the program |

#### CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--interactive`, `-i` | Start in interactive mode | False |
| `--model`, `-m` | Path to GGUF model file | models/zordcoder-v1-q4_k_m.gguf |
| `--context`, `-c` | Context length | 2048 |
| `--threads`, `-t` | Number of CPU threads | 4 |
| `--temperature`, `--temp` | Generation temperature | 0.1 |
| `--max-tokens`, `--max` | Maximum tokens to generate | 1024 |
| `--no-stream` | Disable streaming output | False |
| `--reasoning` | Enable reasoning mode | False |
| `--info` | Show model information | False |
| `--metrics` | Show performance metrics | False |

---

### Next.js Web Interface

The web interface provides a modern chat UI with settings and usage tracking.

#### Architecture

```
Browser (Next.js) --> API Route (/api/chat) --> Python Backend (server.py:8000) --> llama.cpp
```

#### Starting the Web Interface

**Step 1: Start the Python Backend**

```bash
cd zordcoder
python web/server.py
```

The backend runs on http://localhost:8000

**Step 2: Start the Next.js Frontend**

```bash
cd zordcoder/web
npm install
npm run dev
```

The frontend runs on http://localhost:3000

#### Web Interface Features

- Dark/Light theme toggle
- Adjustable temperature (0.0 - 2.0)
- Adjustable max tokens (256 - 4096)
- Reasoning mode toggle
- Real-time usage tracking
- Copy message content
- Clear chat history

#### Environment Variables

Create a `.env` file in the `web/` directory:

```env
BACKEND_URL=http://localhost:8000
```

#### Production Build

```bash
cd zordcoder/web
npm run build
npm start
```

---

## Configuration

### Environment Variables

Set these environment variables to customize behavior:

| Variable | Description | Default |
|----------|-------------|---------|
| `ZORD_MODEL_PATH` | Path to GGUF model file | models/zordcoder-v1-q4_k_m.gguf |
| `ZORD_N_THREADS` | Number of CPU threads | 4 |
| `ZORD_N_GPU_LAYERS` | GPU layers (0 for CPU-only) | 0 |
| `ZORD_N_BATCH` | Batch size for processing | 512 |
| `ZORD_CONTEXT_LENGTH` | Context length | 2048 |
| `ZORD_CACHE_DIR` | Cache directory for model | None |

### Configuration Files

#### GenerationConfig (zord_core.py)

```python
GenerationConfig(
    max_tokens=2048,        # Maximum tokens to generate
    temperature=0.1,        # Sampling temperature (lower = more deterministic)
    top_p=0.9,              # Nucleus sampling threshold
    top_k=40,               # Top-k sampling
    repeat_penalty=1.1,     # Penalty for repeated tokens
    stream=True,            # Enable streaming output
    reasoning_mode=False,   # Enable chain-of-thought reasoning
)
```

#### ZordConfig (zord_core.py)

```python
ZordConfig(
    model_path="models/zordcoder-v1-q4_k_m.gguf",
    n_ctx=2048,             # Context window size
    n_threads=4,            # CPU threads
    n_gpu_layers=0,        # GPU acceleration (0 = CPU only)
    n_batch=512,           # Processing batch size
    temperature=0.1,       # Default temperature
    max_tokens=2048,       # Default max tokens
)
```

---

## API Reference

### Backend Server Endpoints

The Python backend server (`web/server.py`) provides these endpoints:

#### GET /

Health check and server info.

**Response:**
```json
{
  "status": "ok",
  "message": "Zord Coder API v1",
  "model_loaded": true,
  "endpoints": {
    "POST /generate": "Generate response",
    "GET /health": "Health check"
  }
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

#### POST /generate

Generate a response from the model.

**Request Body:**
```json
{
  "prompt": "Write a Python hello world",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Response:**
```json
{
  "response": "print('Hello, World!')",
  "tokens_generated": 25,
  "model": "ZordCoder-v1"
}
```

**Error Responses:**
- `400` - Invalid request (missing prompt)
- `429` - Rate limit exceeded (daily limit reached)
- `500` - Internal server error

### Next.js API Route

#### POST /api/chat

Proxies requests to the Python backend.

**Request Body:**
```json
{
  "message": "Write a Python hello world",
  "temperature": 0.7,
  "maxTokens": 2048
}
```

**Response:**
```json
{
  "response": "print('Hello, World!')",
  "tokens": 25,
  "usage": {
    "messages": 5,
    "tokens": 1500
  }
}
```

---

## Project Structure

```
zordcoder/
├── config/
│   └── merge_config.yaml         # Model merging configuration
├── docs/
│   ├── MODEL_SELECTION.md        # Model selection strategy
│   ├── CONVERSION.md             # GGUF conversion guide
│   └── OPTIMIZATION.md           # Performance optimization
├── logs/
│   └── zord_core.log             # Application logs
├── models/
│   └── zordcoder-v1-q4_k_m.gguf  # GGUF model file (downloaded)
├── scripts/
│   ├── download_model.py         # Auto model downloader
│   ├── setup_termux.sh           # Termux installation script
│   ├── train_zord.py             # nanoGPT training script
│   └── zord_cli.py               # CLI interface
├── src/
│   └── zord_core.py              # Core inference engine
├── web/
│   ├── server.py                 # Python HTTP backend server
│   ├── package.json              # Node.js dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── next.config.js            # Next.js configuration
│   └── src/
│       ├── app/
│       │   ├── page.tsx          # Main chat page
│       │   ├── layout.tsx        # Root layout
│       │   ├── globals.css       # Global styles
│       │   └── api/
│       │       └── chat/
│       │           └── route.ts  # API endpoint
│       └── ...
├── .gitignore
├── README.md
├── requirements.txt              # Python dependencies
└── requirements_web.txt          # Web-specific dependencies
```

---

## Architecture

### Component Overview

```
+------------------+     +------------------+     +------------------+
|   User Interface |     |   API Layer      |     |   Core Engine    |
|                  |     |                  |     |                  |
| - CLI (zord_cli) |---->| - server.py      |---->| - zord_core.py   |
| - Web (Next.js)  |     | - route.ts       |     | - llama.cpp      |
+------------------+     +------------------+     +------------------+
                                                         |
                                                         v
                                                 +------------------+
                                                 |   GGUF Model     |
                                                 | (zordcoder-v1)   |
                                                 +------------------+
```

### Data Flow

1. **User Input** - User enters prompt via CLI or Web UI
2. **API Processing** - Request routed through API layer
3. **Model Inference** - llama.cpp generates response
4. **Streaming** - Tokens streamed back in real-time
5. **Response** - Complete response displayed with metrics

### Key Classes

#### ZordCore (src/zord_core.py)

Main inference engine that handles:
- Model loading and unloading
- Prompt formatting (Llama 3 chat format)
- Text generation with streaming
- Conversation history management
- Performance metrics tracking
- Language detection

#### ZordCLI (scripts/zord_cli.py)

CLI application that provides:
- Interactive terminal interface
- Rich-based UI with syntax highlighting
- Command processing
- Streaming output display

#### ZordEngine (web/server.py)

HTTP server that provides:
- REST API for model inference
- Usage tracking per client
- CORS support for web frontend

---

## Performance

### Benchmarks (Q4_K_M Quantization)

| Metric | Value |
|--------|-------|
| Tokens/second | 15-30 |
| Cold Start | ~3 seconds |
| Memory Usage | ~2GB |
| Context Length | 2048 tokens |
| Model Size | ~833MB |

### Optimization Tips

1. **Reduce Context Length** - Lower memory usage
   ```bash
   export ZORD_CONTEXT_LENGTH=1024
   ```

2. **Increase Threads** - Better CPU utilization
   ```bash
   export ZORD_N_THREADS=8
   ```

3. **Use GPU** - Enable GPU acceleration
   ```bash
   export ZORD_N_GPU_LAYERS=35
   ```

4. **Lower Temperature** - More deterministic outputs
   ```
   Temperature: 0.1 (coding tasks)
   Temperature: 0.7 (creative tasks)
   ```

---

## Troubleshooting

### Model Not Loading

**Symptom:** Error message "Model file not found"

**Solution:**
```bash
# Check if model exists
ls -la models/

# Manually download model
python scripts/download_model.py
```

### Out of Memory

**Symptom:** Application crashes or becomes unresponsive

**Solution:**
```bash
# Reduce context length
export ZORD_CONTEXT_LENGTH=1024

# Reduce batch size
export ZORD_N_BATCH=256
```

### Slow Performance

**Symptom:** Low tokens/second rate

**Solution:**
```bash
# Increase thread count (match CPU cores)
export ZORD_N_THREADS=8

# Check CPU usage
top
```

### Backend Connection Failed (Web UI)

**Symptom:** "Backend not connected" message in web UI

**Solution:**
1. Ensure Python backend is running:
   ```bash
   python web/server.py
   ```

2. Check backend URL in Next.js environment:
   ```env
   BACKEND_URL=http://localhost:8000
   ```

### Import Errors

**Symptom:** ModuleNotFoundError

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# For llama-cpp-python with GPU support
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
```

### Port Already in Use

**Symptom:** "Address already in use" error

**Solution:**
```bash
# Find process using port
# On Linux/Mac:
lsof -i :8000
# On Windows:
netstat -ano | findstr :8000

# Kill process or use different port
python web/server.py --port 8001
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Python: Follow PEP 8 guidelines
- TypeScript: Follow ESLint configuration
- Use meaningful variable and function names
- Add docstrings to functions and classes

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - GGUF quantization and inference
- [nanoGPT](https://github.com/karpathy/nanoGPT) - Training philosophy
- [MergeKit](https://github.com/arcee-ai/mergekit) - Model merging techniques
- [DeepSeek-Coder](https://huggingface.co/deepseek-ai) - Base model architecture
- [Qwen2.5-Coder](https://huggingface.co/Qwen) - Secondary model architecture
- [HuggingFace](https://huggingface.co) - Model hosting and distribution

---

<p align="center">
  <strong>Built by SaJad</strong>
</p>