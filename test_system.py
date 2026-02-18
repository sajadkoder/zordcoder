#!/usr/bin/env python3
"""Test script for Zord Coder"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    print("1. Testing imports...")
    try:
        from llama_cpp import Llama
        print("   llama-cpp-python: OK")
    except ImportError as e:
        print(f"   llama-cpp-python: FAILED - {e}")
        return False
    
    try:
        from rich.console import Console
        print("   rich: OK")
    except ImportError:
        print("   rich: Not installed (optional)")
    
    return True

def test_model():
    print("\n2. Testing model loading...")
    model_path = "models/zordcoder-v1-q4_k_m.gguf"
    if not os.path.exists(model_path):
        print(f"   Model not found at: {model_path}")
        print("   Run: python scripts/download_model.py")
        return False
    
    print(f"   Model found: {model_path}")
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.1f} MB")
    return True

def test_core():
    print("\n3. Testing ZordCore...")
    try:
        from src.zord_core import ZordCore, ZordConfig
        config = ZordConfig()
        print(f"   Config: OK")
        print(f"   Model path: {config.model_path}")
        print(f"   Context: {config.n_ctx}")
        print(f"   Threads: {config.n_threads}")
        return True
    except Exception as e:
        print(f"   FAILED: {e}")
        return False

def test_server():
    print("\n4. Testing API server...")
    import urllib.request
    import json
    
    try:
        with urllib.request.urlopen("http://localhost:8000/", timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"   Status: {data['status']}")
            print(f"   Model loaded: {data['model_loaded']}")
            return True
    except Exception as e:
        print(f"   Server not running: {e}")
        print("   Start with: python web/server.py")
        return False

def main():
    print("=" * 50)
    print("  Zord Coder v1 - System Test")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Model", test_model()))
    results.append(("Core", test_core()))
    results.append(("Server", test_server()))
    
    print("\n" + "=" * 50)
    print("  Results")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed. Check the output above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
