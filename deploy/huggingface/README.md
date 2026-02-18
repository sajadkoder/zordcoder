---
title: Zord Coder v1
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Zord Coder v1

A multilingual coding assistant powered by DeepSeek Coder with GGUF quantization for efficient CPU inference.

## Features

- **Code Generation** - Generate code in Python, JavaScript, TypeScript, C++, Rust, Go, Java, and more
- **CPU Optimized** - Runs efficiently on free CPU instances via llama.cpp
- **REST API** - Simple HTTP API for integration with your applications
- **Rate Limited** - Built-in usage limits (50 messages/day, 50K tokens/day)

## API Usage

### Health Check

```bash
curl https://YOUR_SPACE_NAME.hf.space/health
```

### Generate Code

```bash
curl -X POST https://YOUR_SPACE_NAME.hf.space/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to calculate factorial",
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Response Format

```json
{
  "response": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
  "tokens_generated": 42,
  "model": "ZordCoder-v1"
}
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| prompt | string | required | Your coding question or request |
| temperature | float | 0.7 | Sampling temperature (0.0-1.0) |
| max_tokens | int | 2048 | Maximum tokens to generate |

## Model

This Space uses DeepSeek Coder 1.3B Instruct with Q4_K_M quantization, optimized for CPU inference.

- **Base Model**: [deepseek-ai/deepseek-coder-1.3b-instruct](https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct)
- **Quantization**: GGUF Q4_K_M (~833MB)
- **Inference**: llama.cpp via llama-cpp-python

## Limitations

- Free CPU Spaces may have slower inference (~5-15 tokens/sec)
- Daily usage limits apply per IP address
- Model context limited to 2048 tokens

## License

MIT License

## Credits

Built by [SaJad](https://github.com/sajadkoder)
