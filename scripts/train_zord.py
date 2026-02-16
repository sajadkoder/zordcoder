#!/usr/bin/env python3
"""
Zord Coder v1 - nanoGPT Training Script
Fine-tunes the merged model on high-quality code corpus

Based on Karpathy's nanoGPT philosophy:
- Minimal, readable codebase
- Scalable to large datasets
- Strong GPT fundamentals

Usage:
    python train_zord.py --data_path /path/to/code/corpus --model_path /path/to/merged/model
"""

import os
import sys
import time
import math
import json
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple

import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import GradScaler, autocast

# Try importing transformers for loading base model
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not installed. Install with: pip install transformers")

# Configuration
@dataclass
class TrainConfig:
    # Model
    model_path: str = "./zordcoder-v1-merged"
    tokenizer_path: Optional[str] = None
    
    # Training
    batch_size: int = 8
    max_seq_len: int = 2048
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    betas: Tuple[float, float] = (0.9, 0.95)
    grad_clip: float = 1.0
    
    # Learning rate schedule
    warmup_iters: int = 100
    lr_decay_style: str = "cosine"
    min_lr: float = 1e-5
    
    # Data
    data_path: str = "./data/code_corpus.bin"
    vocab_size: int = 32000
    n_workers: int = 4
    
    # Checkpointing
    checkpoint_interval: int = 500
    save_dir: str = "./checkpoints"
    resume: Optional[str] = None
    
    # Mixed precision
    dtype: str = "bfloat16"
    compile: bool = False
    
    # Device
    device: str = "cuda"
    
    # Logging
    log_interval: int = 10
    verbose: bool = True


class ZordDataset(Dataset):
    """Dataset for code training"""
    
    def __init__(self, data_path: str, block_size: int = 2048):
        self.block_size = block_size
        
        if os.path.exists(data_path):
            # Load preprocessed binary data
            self.data = torch.from_numpy(
                np.fromfile(data_path, dtype=np.uint16)
            ).to(torch.long)
        else:
            # Placeholder: use random data for testing
            print(f"Warning: Data file not found at {data_path}")
            print("Using random data for testing. Replace with real corpus.")
            self.data = torch.randint(0, 32000, (100000,))
        
    def __len__(self):
        return len(self.data) - self.block_size
    
    def __getitem__(self, idx):
        x = self.data[idx:idx + self.block_size]
        y = self.data[idx + 1:idx + self.block_size + 1]
        return x, y


class ZordCausalLM(nn.Module):
    """
    Zord Coder - Simplified GPT model
    Based on nanoGPT architecture
    
    This is used if loading merged model fails
    """
    
    def __init__(self, config: TrainConfig):
        super().__init__()
        self.config = config
        
        # Model architecture (nanoGPT style)
        n_embd = 1024  # Embedding dimension
        n_head = 16   # Number of attention heads
        n_layer = 24  # Number of layers
        vocab_size = config.vocab_size
        
        self.transformer = nn.ModuleDict({
            'wte': nn.Embedding(vocab_size, n_embd),
            'wpe': nn.Embedding(config.max_seq_len, n_embd),
            'drop': nn.Dropout(0.1),
            'h': nn.ModuleList([ZordBlock(n_embd, n_head) for _ in range(n_layer)]),
            'ln_f': nn.LayerNorm(n_embd),
        })
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)
        
        # Weight tying
        self.transformer.wte.weight = self.lm_head.weight
        
        # Initialize weights
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            
    def forward(self, idx, targets=None):
        device = idx.device
        b, t = idx.size()
        
        # Positional embeddings
        pos = torch.arange(0, t, dtype=torch.long, device=device)
        pos_emb = self.transformer.wpe(pos)
        tok_emb = self.transformer.wte(idx)
        
        x = self.transformer.drop(tok_emb + pos_emb)
        
        # Transformer blocks
        for block in self.transformer.h:
            x = block(x)
            
        x = self.transformer.ln_f(x)
        
        # Language modeling head
        logits = self.lm_head(x)
        
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=-1
            )
            
        return logits, loss
    
    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        """Generate new tokens"""
        for _ in range(max_new_tokens):
            idx_cond = idx if idx.size(1) <= self.config.max_seq_len else idx[:, -self.config.max_seq_len:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
                
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
            
        return idx


class ZordBlock(nn.Module):
    """Transformer block with pre-norm and SwiGLU"""
    
    def __init__(self, n_embd: int, n_head: int):
        super().__init__()
        self.ln_1 = nn.LayerNorm(n_embd)
        self.attn = nn.MultiheadAttention(n_embd, n_head, batch_first=True, dropout=0.1)
        self.ln_2 = nn.LayerNorm(n_embd)
        
        # SwiGLU MLP
        hidden_dim = 4 * n_embd
        self.mlp = nn.ModuleDict({
            'c_fc': nn.Linear(n_embd, hidden_dim),
            'c_proj': nn.Linear(hidden_dim, n_embd),
            'dropout': nn.Dropout(0.1),
        })
        
    def forward(self, x):
        # Pre-norm attention
        attn_out, _ = self.attn(self.ln_1(x), self.ln_1(x), self.ln_1(x))
        x = x + attn_out
        
        # SwiGLU MLP
        x = x + self.mlp.dropout(self.mlp.c_proj(F.silu(self.mlp.c_fc(self.ln_2(x)))))
        
        return x


def load_model(config: TrainConfig):
    """Load the merged model or create a new one"""
    
    if os.path.exists(config.model_path):
        try:
            if TRANSFORMERS_AVAILABLE:
                print(f"Loading model from {config.model_path}")
                model = AutoModelForCausalLM.from_pretrained(
                    config.model_path,
                    torch_dtype=torch.bfloat16 if config.device == "cuda" else torch.float32,
                    device_map=config.device,
                    trust_remote_code=True
                )
                print("Model loaded successfully!")
                return model
        except Exception as e:
            print(f"Failed to load merged model: {e}")
            print("Creating new nanoGPT model instead...")
    
    print("Initializing new Zord Coder model...")
    return ZordCausalLM(config)


def get_lr(it: int, config: TrainConfig):
    """Learning rate schedule with warmup"""
    if it < config.warmup_iters:
        return config.learning_rate * it / config.warmup_iters
    
    if config.lr_decay_style == "cosine":
        decay_ratio = (it - config.warmup_iters) / (config.max_iters - config.warmup_iters)
        return config.min_lr + (config.learning_rate - config.min_lr) * 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    else:
        return config.learning_rate


def train_step(model, batch, optimizer, scaler, config: TrainConfig):
    """Single training step"""
    model.train()
    
    x, y = batch
    x = x.to(config.device)
    y = y.to(config.device)
    
    optimizer.zero_grad()
    
    # Mixed precision forward pass
    with autocast(dtype=torch.bfloat16):
        logits, loss = model(x, y)
    
    # Backward pass
    scaler.scale(loss).backward()
    
    # Gradient clipping
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_clip)
    
    # Optimizer step
    scaler.step(optimizer)
    scaler.update()
    
    return loss.item()


@torch.no_grad()
def evaluate(model, dataloader, config: TrainConfig):
    """Evaluate model on validation set"""
    model.eval()
    total_loss = 0
    num_batches = 0
    
    for batch in dataloader:
        x, y = batch
        x = x.to(config.device)
        y = y.to(config.device)
        
        logits, loss = model(x, y)
        total_loss += loss.item()
        num_batches += 1
        
    return total_loss / num_batches


def save_checkpoint(model, optimizer, scaler, iteration, config: TrainConfig):
    """Save training checkpoint"""
    save_path = os.path.join(config.save_dir, f"checkpoint_{iteration}.pt")
    os.makedirs(config.save_dir, exist_ok=True)
    
    checkpoint = {
        'iteration': iteration,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scaler_state_dict': scaler.state_dict(),
        'config': config,
    }
    
    torch.save(checkpoint, save_path)
    print(f"Checkpoint saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Train Zord Coder v1")
    parser.add_argument("--model_path", type=str, default="./zordcoder-v1-merged")
    parser.add_argument("--data_path", type=str, default="./data/code_corpus.bin")
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--max_seq_len", type=int, default=2048)
    parser.add_argument("--max_iters", type=int, default=10000)
    parser.add_argument("--learning_rate", type=float, default=1e-4)
    parser.add_argument("--save_dir", type=str, default="./checkpoints")
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    
    args = parser.parse_args()
    
    # Create config
    config = TrainConfig(
        model_path=args.model_path,
        data_path=args.data_path,
        batch_size=args.batch_size,
        max_seq_len=args.max_seq_len,
        learning_rate=args.learning_rate,
        max_iters=args.max_iters,
        save_dir=args.save_dir,
        resume=args.resume,
        device=args.device,
    )
    
    print("=" * 60)
    print("Zord Coder v1 - Training")
    print("=" * 60)
    print(f"Device: {config.device}")
    print(f"Batch size: {config.batch_size}")
    print(f"Max sequence length: {config.max_seq_len}")
    print(f"Max iterations: {config.max_iters}")
    print(f"Learning rate: {config.learning_rate}")
    print("=" * 60)
    
    # Load model
    model = load_model(config)
    model = model.to(config.device)
    
    # Compile model if requested
    if config.compile and hasattr(torch, 'compile'):
        print("Compiling model...")
        model = torch.compile(model)
    
    # Create dataloader
    dataset = ZordDataset(config.data_path, config.max_seq_len)
    dataloader = DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.n_workers,
        pin_memory=True,
    )
    
    # Optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
        betas=config.betas,
    )
    
    # Mixed precision scaler
    scaler = GradScaler()
    
    # Resume from checkpoint if requested
    start_iteration = 0
    if config.resume:
        checkpoint = torch.load(config.resume)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scaler.load_state_dict(checkpoint['scaler_state_dict'])
        start_iteration = checkpoint['iteration'] + 1
        print(f"Resumed from iteration {start_iteration}")
    
    # Training loop
    print("\nStarting training...")
    iteration = start_iteration
    
    try:
        data_iter = iter(dataloader)
        
        while iteration < config.max_iters:
            # Get batch
            try:
                batch = next(data_iter)
            except StopIteration:
                data_iter = iter(dataloader)
                batch = next(data_iter)
            
            # Training step
            loss = train_step(model, batch, optimizer, scaler, config)
            
            # Learning rate
            lr = get_lr(iteration, config)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr
            
            # Logging
            if iteration % config.log_interval == 0:
                print(f"Iter {iteration} | Loss: {loss:.4f} | LR: {lr:.2e}")
            
            # Checkpointing
            if iteration % config.checkpoint_interval == 0 and iteration > 0:
                save_checkpoint(model, optimizer, scaler, iteration, config)
            
            iteration += 1
            
    except KeyboardInterrupt:
        print("\nTraining interrupted. Saving checkpoint...")
        save_checkpoint(model, optimizer, scaler, iteration, config)
    
    print("\nTraining complete!")
    save_checkpoint(model, optimizer, scaler, iteration, config)


if __name__ == "__main__":
    main()
