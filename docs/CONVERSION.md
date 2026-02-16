# Zord Coder v1 - Model Conversion Guide

This guide explains how to convert your trained/merged model to GGUF format for optimal Termux deployment.

## Prerequisites

```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

## Conversion Methods

### Method 1: Using llama.cpp (Recommended)

Convert HuggingFace format to GGUF:

```bash
# Clone your model from HuggingFace
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained('your-model-name')
tokenizer = AutoTokenizer.from_pretrained('your-model-name')

model.save_pretrained('./zordcoder-v1')
tokenizer.save_pretrained('./zordcoder-v1')
"

# Convert to GGUF using llama.cpp
python llama.cpp/convert.py ./zordcoder-v1 \
    --outfile ./zordcoder-v1-f16.gguf \
    --outtype f16
```

### Method 2: Using convert.py with Quantization

```bash
# Convert and quantize in one step
python llama.cpp/convert.py ./zordcoder-v1 \
    --outfile ./zordcoder-v1-q4_k_m.gguf \
    --quantize q4_k_m
```

### Quantization Types

| Type | Size (1.5B) | Quality | Speed |
|------|-------------|---------|-------|
| Q2_K | ~500MB | Low | Fastest |
| Q3_K_S | ~650MB | Medium | Fast |
| Q4_0 | ~900MB | Good | Fast |
| **Q4_K_M** | ~950MB | **Recommended** | Fast |
| Q5_K_S | ~1.1GB | Very Good | Medium |
| Q5_K_M | ~1.2GB | Excellent | Medium |
| Q6_K | ~1.4GB | Near Perfect | Slower |
| F16 | ~3GB | Perfect | Slow |

**Recommended for mobile: Q4_K_M**

### Method 3: Using Python Script

```python
from llama_cpp import convert_to_gguf

# Convert model to GGUF
convert_to_gguf(
    input_model_path="./zordcoder-v1",
    output_model_path="./zordcoder-v1-q4_k_m.gguf",
    model_type="llama",
    quantization="q4_k_m"
)
```

## Verification

Verify your GGUF file:

```bash
# Check file size
ls -lh zordcoder-v1-q4_k_m.gguf

# Test with llama-cli (if available)
./llama.cpp/llama-cli -m zordcoder-v1-q4_k_m.gguf -n 50 -p "Hello"
```

## Troubleshooting

### Out of Memory During Conversion

```bash
# Use lower precision
python llama.cpp/convert.py ./zordcoder-v1 \
    --outfile ./zordcoder-v1-q4.gguf \
    --outtype q4_0 \
    --memory-f16
```

### Tokenizer Issues

If tokenizer not loading properly:

```bash
# Add tokenizer config explicitly
python llama.cpp/convert.py ./zordcoder-v1 \
    --outfile ./zordcoder-v1-q4_k_m.gguf \
    -- tokenizer.json ./zordcoder-v1/tokenizer.json
```

## Model Sources

Pre-quantized models available at:
- [TheBloke (DeepSeek-Coder)](https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF)
- [TheBloke (Qwen2.5)](https://huggingface.co/TheBloke/Qwen2-1.5B-Instruct-GGUF)
- [lmstudio community](https://huggingface.co/lmstudio-community)

## Copy to Termux

```bash
# Copy model to phone
adb push zordcoder-v1-q4_k_m.gguf /sdcard/zordcoder/models/

# Or use Termux file manager
# Navigate to: ~/zordcoder/models/
```
