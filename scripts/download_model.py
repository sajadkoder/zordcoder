#!/usr/bin/env python3
"""
Zord Coder v1 - Auto Model Downloader
Downloads the GGUF model automatically if not found
"""

import os
import sys
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


# Default model configuration
DEFAULT_MODEL_REPO = "TheBloke/deepseek-coder-1.3b-instruct-GGUF"
DEFAULT_MODEL_FILE = "deepseek-coder-1.3b-instruct-q4_k_m.gguf"


def get_model_path():
    """Get the model path from environment or default"""
    # Check environment variable
    model_path = os.getenv("ZORD_MODEL_PATH")
    if model_path:
        return model_path
    
    # Default path
    script_dir = Path(__file__).parent.parent
    return str(script_dir / "models" / "zordcoder-v1-q4_k_m.gguf")


def download_model(force=False):
    """
    Download model if not exists
    """
    model_path = get_model_path()
    
    # Check if already exists
    if os.path.exists(model_path) and not force:
        print(f"✓ Model found: {model_path}")
        return model_path
    
    # Create models directory
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    if not HF_AVAILABLE:
        print("Installing huggingface_hub...")
        os.system(f"{sys.executable} -m pip install huggingface_hub")
        from huggingface_hub import hf_hub_download
    
    print(f"⬇ Downloading model from HuggingFace...")
    print(f"   Repo: {DEFAULT_MODEL_REPO}")
    print(f"   File: {DEFAULT_MODEL_FILE}")
    print(f"   This may take a few minutes...")
    
    try:
        downloaded_path = hf_hub_download(
            repo_id=DEFAULT_MODEL_REPO,
            filename=DEFAULT_MODEL_FILE,
            local_dir=os.path.dirname(model_path),
            local_dir_use_symlinks=False,
        )
        
        # Rename to our naming convention
        if downloaded_path != model_path:
            if os.path.exists(model_path):
                os.remove(model_path)
            os.rename(downloaded_path, model_path)
        
        print(f"✓ Model downloaded successfully!")
        print(f"   Saved to: {model_path}")
        return model_path
        
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return None


def check_and_download():
    """Main entry point - check and download if needed"""
    model_path = get_model_path()
    
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✓ Model ready: {model_path} ({size_mb:.1f} MB)")
        return model_path
    
    print("⚠ Model not found!")
    print(f"   Expected: {model_path}")
    print()
    
    return download_model()


if __name__ == "__main__":
    check_and_download()
