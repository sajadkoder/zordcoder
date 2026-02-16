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
- 🌐 **Multi-Language** - Python, JavaScript, TypeScript, C++, Rust, Go, Java, Bash, and more
- 💬 **Interactive CLI** - Beautiful terminal interface with syntax highlighting
- 🔄 **Streaming Output** - Real-time token generation
- 🧠 **Reasoning Mode** - Chain-of-thought like DeepSeek-R1
- 📱 **Termux Ready** - Optimized for Android devices

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sajadkoder/zordcoder.git
cd zordcoder
```

### 2. Download a Model

Download a GGUF model (recommended: Q4_K_M quantization):

```bash
# Create models directory
mkdir -p models

# Download DeepSeek-Coder-1.3B (recommended)
# From: https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF
# Or use huggingface-cli:
huggingface-cli download TheBloke/deepseek-coder-1.3b-instruct-GGUF \
    deepseek-coder-1.3b-instruct-q4_k_m.gguf \
    --local-dir ./models
```

### 3. Run the CLI

```bash
# Using Python directly
python3 scripts/zord_cli.py

# Or install and use
pip install -e .
zord
```

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
├── config/
│   └── merge_config.yaml      # Model merging configuration
├── docs/
│   ├── MODEL_SELECTION.md    # Model selection strategy
│   ├── CONVERSION.md         # GGUF conversion guide
│   └── OPTIMIZATION.md       # Performance optimization
├── scripts/
│   ├── setup_termux.sh       # Termux installation script
│   ├── train_zord.py         # nanoGPT training script
│   └── zord_cli.py           # CLI interface
├── src/
│   └── zord_core.py          # Core inference engine
├── .gitignore
├── README.md
└── requirements.txt
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
  <strong>Built with ❤️ for mobile coding</strong>
</p>
