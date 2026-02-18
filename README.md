# Zord Coder v1

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Platform-Termux-orange" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.9+-yellow" alt="Python">
</p>

> **Zord Coder v1** - The ultimate multilingual coding assistant optimized for Android Termux. Built with model merging techniques, nanoGPT philosophy, and blazing-fast GGUF inference.

## Features

- 🚀 **Blazing Fast** - Optimized GGUF quantization for mobile devices
- 🌐 **Web Interface** - Beautiful Next.js web UI (self-hosted)
- 💻 **CLI** - Terminal interface for developers
- 🌐 **Multi-Language** - Python, JavaScript, TypeScript, C++, Rust, Go, Java, Bash, and more
- 💬 **Interactive Chat** - Beautiful chat interface with code highlighting
- 🔄 **Streaming** - Real-time token generation
- 🧠 **Reasoning Mode** - Chain-of-thought like DeepSeek-R1
- 📱 **Termux Ready** - Optimized for Android devices
- 🎨 **x.ai Theme** - Beautiful dark/light themes

## Choose Your Interface

### Option 1: Next.js Web (Recommended)
Modern, professional web UI with React + Next.js

```bash
cd web
npm install
npm run dev
```
Visit: http://localhost:3000

### Option 2: Streamlit Web
Simple Python-based web UI

```bash
pip install -r requirements_web.txt
streamlit run web_app.py
```
Visit: http://localhost:8501

### Option 3: Terminal (CLI)
For developers who prefer command line

```bash
pip install -r requirements.txt
python scripts/zord_cli.py --interactive
```

## Quick Start

### 1. Clone & Run

```bash
git clone https://github.com/sajadkoder/zordcoder.git
cd zordcoder
pip install -r requirements.txt
python scripts/zord_cli.py --interactive
```

The model will download automatically on first run!

> **Note:** First run will download the model (~833MB) automatically from HuggingFace.

## Web Interface

### Run Web App

```bash
# Install web dependencies
pip install -r requirements_web.txt

# Run the web app
streamlit run web_app.py
# or
python web_app.py
```

The web app will open at `http://localhost:8501`

### Features
- 🌐 **Beautiful Web UI** - Modern chat interface
- 🎨 **x.ai Theme** - Dark/Light mode with green accents
- 💬 **Chat History** - Persistent conversation
- ⚡ **Streaming** - Real-time responses
- ⚙️ **Settings** - Temperature, max tokens, reasoning mode
- 📊 **Usage Limits** - 50 messages/day, 50K tokens/day (free tier)
- 🚫 **No Auth Required** - Anyone can use

### Making It Public

To share your Zord Coder with the world:

```bash
# Option 1: Cloudflare Tunnel (Free)
pip install cloudflared
cloudflared tunnel --url http://localhost:8501

# Option 2: ngrok
pip install ngrok
ngrok http 8501
```

Your URL will be something like: `https://your-tunnel.cloudflare.link`

## Prerequisites

- Python 3.9+
- Windows, Linux, or Termux (Android)
- Internet connection (for first run - model download)
- 2GB+ free storage space

## Installation (Termux)

```bash
# Run the setup script
bash scripts/setup_termux.sh

# Or manual installation
pkg update && pkg install python git
pip install -r requirements.txt

# Download model and run
python3 scripts/zord_cli.py --interactive
```

## Usage

### Interactive Mode

```bash
python3 scripts/zord_cli.py --interactive
```

### Single Prompt

```bash
python3 scripts/zord_cli.py "Write a Python hello world"
```

### With Custom Settings

```bash
python3 scripts/zord_cli.py "Explain recursion" \
    --temperature 0.2 \
    --max-tokens 512 \
    --context 2048
```

## Commands

| Command | Description |
|---------|-------------|
| `clear` | Clear conversation history |
| `reasoning` | Toggle reasoning mode |
| `stream` | Toggle streaming mode |
| `metrics` | Show performance metrics |
| `history` | Show conversation history |
| `language <lang>` | Set preferred language |
| `help` | Show help message |
| `exit` | Exit the program |

## Project Structure

```
zordcoder/
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── config/
│   └── merge_config.yaml    # Model merging configuration
├── docs/
│   ├── MODEL_SELECTION.md   # Model selection strategy
│   ├── CONVERSION.md        # GGUF conversion guide
│   └── OPTIMIZATION.md     # Performance optimization
├── scripts/
│   ├── setup_termux.sh     # Termux installation script
│   ├── train_zord.py       # nanoGPT training script
│   ├── download_model.py    # Auto model downloader
│   └── zord_cli.py        # CLI interface
├── src/
│   └── zord_core.py       # Core inference engine
├── web_app.py              # Streamlit web application
├── .gitignore
├── README.md
├── requirements.txt         # Main dependencies
└── requirements_web.txt    # Web dependencies
```

## Documentation

- [Model Selection Strategy](docs/MODEL_SELECTION.md)
- [GGUF Conversion Guide](docs/CONVERSION.md)
- [Performance Optimization](docs/OPTIMIZATION.md)

## System Requirements

### Minimum
- Android 7.0+
- 3GB RAM
- 2GB Storage

### Recommended
- Android 10+
- 6GB+ RAM
- 4GB+ Storage

## Model Merging

Zord Coder v1 uses state-of-the-art model merging techniques:

- **TIES (Task Interference Elimination)**
- **DARE (Data-Aware Reward Estimation)**
- **SLERP** interpolation

See [MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for details.

## Performance

| Metric | Value |
|--------|-------|
| Tokens/sec | 15-30 (Q4_K_M) |
| Cold Start | ~3 seconds |
| Memory Usage | ~2GB (Q4_K_M) |
| Context Length | 2048 tokens |

## Troubleshooting

### Model Not Loading

```bash
# Check model file
ls -la models/

# Verify file
file models/zordcoder-v1-q4_k_m.gguf
```

### Out of Memory

```bash
# Reduce context in config
export ZORD_CONTEXT_LENGTH=1024
```

### Slow Performance

See [OPTIMIZATION.md](docs/OPTIMIZATION.md) for tuning tips.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - GGUF quantization
- [nanoGPT](https://github.com/karpathy/nanoGPT) - Training philosophy
- [MergeKit](https://github.com/arcee-ai/mergekit) - Model merging
- [DeepSeek-Coder](https://huggingface.co/deepseek-ai) - Base model
- [Qwen2.5-Coder](https://huggingface.co/Qwen) - Secondary model

---

<p align="center">
  <strong>Built with ❤️ by sajad</strong>
</p>
