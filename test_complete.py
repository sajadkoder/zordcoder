#!/usr/bin/env python3
"""
Zord Coder v1 - Complete Test Suite
Tests all components and runs an end-to-end test
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.error

# Configuration
SERVER_URL = "http://localhost:8000"
SERVER_STARTUP_TIME = 8  # seconds

def print_header(title):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def print_test(name, passed):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} {name}")
    return passed

def test_python_with_llama():
    """Find Python with llama-cpp-python"""
    print_header("1. Finding Python with llama-cpp-python")
    
    candidates = [
        r"C:\Users\abdul\miniconda3\python.exe",
        r"C:\Python312\python.exe",
        r"C:\Python311\python.exe",
        r"C:\Python310\python.exe",
        "python",
    ]
    
    for py in candidates:
        try:
            result = subprocess.run(
                [py, "-c", "import llama_cpp; print('OK')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "OK" in result.stdout:
                print(f"  Found: {py}")
                return py
        except Exception:
            continue
    
    print("  ERROR: No Python with llama-cpp-python found!")
    return None

def test_model_exists(python_exe):
    """Test if model file exists"""
    print_header("2. Testing Model File")
    
    model_path = "models/zordcoder-v1-q4_k_m.gguf"
    
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"  Model: {model_path}")
        print(f"  Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"  Model not found: {model_path}")
        print("  Run: python scripts/download_model.py")
        return False

def test_core_imports(python_exe):
    """Test that core module can be imported"""
    print_header("3. Testing Core Module")
    
    try:
        result = subprocess.run(
            [python_exe, "-c", "from src.zord_core import ZordCore, ZordConfig; print('OK')"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="C:\\Users\\abdul\\zordcoder"
        )
        if result.returncode == 0 and "OK" in result.stdout:
            print("  Core module imports: OK")
            return True
        else:
            print(f"  Import error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def start_server(python_exe):
    """Start the API server"""
    print_header("4. Starting API Server")
    
    try:
        process = subprocess.Popen(
            [python_exe, "web/server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd="C:\\Users\\abdul\\zordcoder"
        )
        
        print(f"  Starting server (PID: {process.pid})...")
        
        # Wait for server to start
        for i in range(SERVER_STARTUP_TIME * 2):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen(f"{SERVER_URL}/health", timeout=2) as response:
                    data = json.loads(response.read().decode())
                    if data.get("model_loaded"):
                        print("  Server started successfully!")
                        return process
            except Exception:
                continue
        
        print("  Server failed to start in time")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"  Error starting server: {e}")
        return None

def test_api_endpoints():
    """Test all API endpoints"""
    print_header("5. Testing API Endpoints")
    
    results = []
    
    # Test GET /
    try:
        with urllib.request.urlopen(f"{SERVER_URL}/", timeout=5) as response:
            data = json.loads(response.read().decode())
            results.append(print_test("GET / endpoint", data.get("status") == "ok"))
    except Exception as e:
        results.append(print_test("GET / endpoint", False))
        print(f"    Error: {e}")
    
    # Test GET /health
    try:
        with urllib.request.urlopen(f"{SERVER_URL}/health", timeout=5) as response:
            data = json.loads(response.read().decode())
            results.append(print_test("GET /health endpoint", data.get("status") == "ok"))
    except Exception as e:
        results.append(print_test("GET /health endpoint", False))
        print(f"    Error: {e}")
    
    # Test POST /generate
    try:
        req = urllib.request.Request(
            f"{SERVER_URL}/generate",
            data=json.dumps({
                "prompt": "Say hello",
                "temperature": 0.1,
                "max_tokens": 20
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            has_response = bool(data.get("response"))
            results.append(print_test("POST /generate endpoint", has_response))
            if has_response:
                print(f"    Response: {data['response'][:50]}...")
    except Exception as e:
        results.append(print_test("POST /generate endpoint", False))
        print(f"    Error: {e}")
    
    return all(results)

def test_cli(python_exe):
    """Test CLI with a single prompt"""
    print_header("6. Testing CLI")
    
    try:
        result = subprocess.run(
            [python_exe, "scripts/zord_cli.py", "Say hello", "--max-tokens", "20", "--no-stream"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="C:\\Users\\abdul\\zordcoder"
        )
        
        if result.returncode == 0:
            # Check if there's actual content
            output = result.stdout + result.stderr
            has_response = "Response:" in output or len(output) > 100
            print_test("CLI execution", has_response)
            return has_response
        else:
            print(f"  CLI error: {result.stderr[:200]}")
            print_test("CLI execution", False)
            return False
    except Exception as e:
        print(f"  Error: {e}")
        print_test("CLI execution", False)
        return False

def stop_server(process):
    """Stop the API server"""
    print_header("7. Stopping Server")
    
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
            print("  Server stopped cleanly")
        except subprocess.TimeoutExpired:
            process.kill()
            print("  Server killed (timeout)")
    else:
        print("  No server to stop")

def main():
    print("=" * 50)
    print("  Zord Coder v1 - Complete Test Suite")
    print("=" * 50)
    
    # Find Python
    python_exe = test_python_with_llama()
    if not python_exe:
        print("\nFAILED: Cannot proceed without Python with llama-cpp-python")
        return 1
    
    # Run tests
    server_process = None
    results = []
    
    try:
        results.append(("Model File", test_model_exists(python_exe)))
        results.append(("Core Module", test_core_imports(python_exe)))
        
        # Start server for API tests
        server_process = start_server(python_exe)
        if server_process:
            results.append(("API Endpoints", test_api_endpoints()))
            results.append(("CLI", test_cli(python_exe)))
        else:
            results.append(("API Endpoints", False))
            results.append(("CLI", False))
        
    finally:
        stop_server(server_process)
    
    # Print summary
    print_header("Summary")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("  ALL TESTS PASSED!")
    else:
        print("  SOME TESTS FAILED")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
