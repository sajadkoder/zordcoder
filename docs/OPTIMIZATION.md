# Zord Coder v1 - Performance Optimization Guide

This guide helps you optimize Zord Coder for smooth performance on mid-range Android devices.

## Device Recommendations

### Minimum Requirements
- **RAM**: 3GB available
- **Storage**: 2GB free space
- **Android**: 7.0+ (Termux supported)

### Recommended
- **RAM**: 6GB+ available
- **Storage**: 4GB+ free space
- **Android**: 10+

## Thread Management

### Optimal Thread Count

```bash
# Set based on CPU cores
export OMP_NUM_THREADS=4  # For 4-core device
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4
```

### Determining CPU Cores

```bash
# Check available cores
nproc

# Or in Python
import os
print(os.cpu_count())
```

### Recommended Settings

| Device RAM | n_threads | n_batch | context |
|------------|-----------|---------|---------|
| 3GB | 2 | 256 | 1024 |
| 4GB | 3 | 384 | 1536 |
| 6GB | 4 | 512 | 2048 |
| 8GB+ | 4-6 | 512 | 2048 |

## Memory Optimization

### Reduce Context Length

```python
# In zord_core.py or config
config = ZordConfig(
    n_ctx=1024,  # Reduce from 2048
    n_keep=512,  # Keep only recent context
)
```

### Clear Cache Regularly

```bash
# Add to your workflow
python -c "
import gc
gc.collect()
"
```

### Use KV Cache Quantization

```python
# Enable in config
config = ZordConfig(
    kv_cache_quantization=True,  # Reduces memory ~40%
)
```

## Generation Settings

### Fast Response Settings

```python
config = GenerationConfig(
    temperature=0.1,
    top_p=0.9,
    top_k=40,
    repeat_penalty=1.1,
    # Lower for faster generation
    max_tokens=512,  # Start small, increase if needed
)
```

### Quality Settings

```python
config = GenerationConfig(
    temperature=0.2,
    top_p=0.95,
    top_k=50,
    repeat_penalty=1.15,
    max_tokens=2048,  # Full generation
)
```

## Thermal Throttling Prevention

### Avoid Continuous Use

```bash
# Add delays between queries
sleep 5

# Use smaller max_tokens
```

### Monitor Temperature

```bash
# In Termux
termux-battery-status
```

## Optimization Script

Create `optimize_zord.sh`:

```bash
#!/bin/bash
# Zord Coder - Performance Optimization Script

echo "⚡ Optimizing Zord Coder for your device..."

# Detect CPU cores
CORES=$(nproc)
echo "📱 CPU Cores: $CORES"

# Calculate optimal threads (leave 1 core for system)
THREADS=$((CORES > 1 ? CORES - 1 : 1))

# Set thread count
export OMP_NUM_THREADS=$THREADS
export OPENBLAS_NUM_THREADS=$THREADS
export MKL_NUM_THREADS=$THREADS
export NUMEXPR_NUM_THREADS=$THREADS

echo "🔧 Threads: $THREADS"

# Python optimization
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# llama.cpp
export LLAMA_CPP_NO_GPU=1
export LLAMA_CPP_MAX_THREADS=$THREADS

# Memory
export PYTHONMALLOC=mem_debug  # Only for debugging

echo "✅ Optimization complete!"
echo ""
echo "Settings applied:"
echo "  Threads: $THREADS"
echo "  Python: optimized"
echo "  llama.cpp: CPU only"
```

Run it:
```bash
bash optimize_zord.sh
```

## Profiling

### Check Memory Usage

```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Benchmark Script

```python
import time
from zord_core import ZordCore, ZordConfig, GenerationConfig

config = ZordConfig()
engine = ZordCore(config)
engine.load_model()

prompts = [
    "Hello",
    "Write Python hello world",
    "Explain what is recursion",
]

for prompt in prompts:
    start = time.time()
    response, metrics = engine.generate_response(prompt)
    print(f"Prompt: {prompt[:30]}...")
    print(f"Time: {metrics['generation_time']:.2f}s")
    print(f"Tokens: {metrics['tokens_generated']}")
    print(f"Speed: {metrics['tokens_per_second']:.1f} tok/s")
    print()
```

## Common Issues

### Slow Generation

**Solution:**
1. Reduce context length
2. Reduce n_threads
3. Use Q4 quantization
4. Check for thermal throttling

### Out of Memory

**Solution:**
1. Reduce n_ctx to 1024
2. Reduce n_batch to 256
3. Enable kv_cache_quantization
4. Clear conversation history

### Model Not Loading

**Solution:**
1. Check file exists: `ls -la models/`
2. Check file not corrupted: `file models/zordcoder-v1-q4_k_m.gguf`
3. Verify GGUF format
4. Check storage space: `df -h`

## Quick Reference

| Issue | Solution |
|-------|----------|
| Too slow | Reduce threads, context |
| Out of memory | Reduce n_ctx, enable quantization |
| Thermal issues | Reduce max_tokens, add delays |
| Loading fails | Check file, restart Termux |
