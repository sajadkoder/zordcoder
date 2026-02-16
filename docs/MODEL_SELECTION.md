# Zord Coder v1 - Model Selection Strategy

## Executive Summary

This document outlines the model selection strategy for creating Zord Coder v1 - a multilingual coding assistant optimized for Android Termux deployment.

## Base Model Candidates

We selected small, compatible architectures (<2B parameters) that share common characteristics and can be effectively merged/fused:

### Primary Base: DeepSeek-Coder Family

| Model | HuggingFace ID | Parameters | Strength |
|-------|---------------|------------|----------|
| DeepSeek-Coder-1.3B-Instruct | `deepseek-ai/deepseek-coder-1.3b-instruct` | 1.3B | Excellent code generation, infilling |
| DeepSeek-Coder-1.5B-Base | `deepseek-ai/deepseek-coder-1.5b-base` | 1.5B | Strong pretraining foundation |

**Why DeepSeek?**
- Native code completion and infilling capabilities
- Multi-language code understanding (50+ languages)
- Efficient architecture for mobile deployment

### Secondary: Qwen2.5-Coder Family

| Model | HuggingFace ID | Parameters | Strength |
|-------|---------------|------------|----------|
| Qwen2.5-Coder-1.5B-Instruct | `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | Superior language understanding |
| Qwen2.5-Coder-1.5B-Base | `Qwen/Qwen2.5-1.5B` | 1.5B | Strong general foundation |

**Why Qwen2.5?**
- Excellent Chinese-English bilingual support
- Enhanced instruction following
- Efficient inference on mobile

### Tertiary: GLM Variants

| Model | HuggingFace ID | Parameters | Strength |
|-------|---------------|------------|----------|
| GLM-4-9B-Chat | `THUDM/glm-4-9b-chat` | 9B (use 4B variant) | Autoregressive blank infilling |
| ChatGLM3-6B | `THUDM/chatglm3-6b` | 6B | Efficient dialogue understanding |

**Note**: For mobile deployment, we use smaller GLM-4 variants or extract layers for merging.

**Why GLM?**
- Unique blank infilling pretraining objective
- Strong bilingual (Chinese-English) capabilities
- Efficient parameter utilization

### Alternative: Code-Specific Models

| Model | HuggingFace ID | Parameters | Strength |
|-------|---------------|------------|----------|
| CodeQwen1.5-1.8B | `Qwen/CodeQwen1.5-1.8B` | 1.8B | Dedicated code generation |
| Phi-2-Coder | `microsoft/phi-2` | 2.7B | Knowledge distillation base |

## Selected Model Combination for Zord Coder v1

### Recommended Configuration

```
Base Model: deepseek-ai/deepseek-coder-1.3b-instruct (60% weight)
Secondary:  Qwen/Qwen2.5-1.5B-Instruct (25% weight)
Tertiary:  THUDM/chatglm3-6b (15% weight) - extract layers
```

### Architecture Compatibility

All selected models share:
- **Transformer decoder-only architecture**
- **RMSNorm** normalization (or LayerNorm)
- **SwiGLU** or **GELU** activations
- **RoPE** position embeddings
- **Similar tokenizer** (Byte-level BPE)

This ensures mathematical compatibility for merging.

## Strength Infusion Strategy

### From DeepSeek-Coder:
- **Code completion**: Native infilling with `<| fills |>`
- **Repo-level understanding**: Multi-file context
- **MoE-inspired routing**: Knowledge expert selection

### From Qwen2.5:
- **Instruction tuning**: Better user intent understanding
- **Multi-language**: Enhanced non-English code support
- **System prompts**: Better prompt adherence

### From GLM:
- **Blank infilling**: Flexible code generation patterns
- **Bilingual support**: Chinese-English code comments
- **Efficient attention**: Sliding window variants

## Final Model Specifications

| Parameter | Value |
|-----------|-------|
| Total Parameters | ~1.5B (after merging/distillation) |
| Context Length | 4096 tokens |
| Quantized Size | ~900MB (Q4_K_M) |
| Target Languages | Python, JS, TS, C++, Rust, Go, Java, Bash |
| Mobile RAM Target | 3-4GB |

## References

1. DeepSeek-Coder: https://huggingface.co/deepseek-ai
2. Qwen2.5-Coder: https://huggingface.co/Qwen
3. GLM-4: https://huggingface.co/THUDM
4. Model Merging: https://arxiv.org/abs/2406.11781
5. TIES Merging: https://arxiv.org/abs/2306.01708
