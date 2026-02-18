#!/usr/bin/env python3
"""
Zord Coder v1 - HuggingFace Spaces Entry Point
Downloads model and starts the server
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("Error: llama-cpp-python not installed")

try:
    from huggingface_hub import hf_hub_download
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Error: huggingface-hub not installed")


MODEL_REPO = os.getenv("MODEL_REPO", "TheBloke/deepseek-coder-1.3b-instruct-GGUF")
MODEL_FILE = os.getenv("MODEL_FILE", "deepseek-coder-1.3b-instruct-q4_k_m.gguf")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/model.gguf")
PORT = int(os.getenv("PORT", "7860"))
HOST = os.getenv("HOST", "0.0.0.0")


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 7860
    model_path: str = "/app/models/model.gguf"
    n_ctx: int = 2048
    n_threads: int = 4
    n_gpu_layers: int = 0


class UsageTracker:
    """Track API usage per client"""
    
    def __init__(self):
        self.usage: Dict[str, Dict[str, Any]] = {}
        self.daily_limit_messages = 50
        self.daily_limit_tokens = 50000
    
    def get_client_id(self, handler) -> str:
        client = handler.client_address[0]
        return f"{client}"
    
    def check_limit(self, client_id: str) -> tuple:
        today = datetime.now().date().isoformat()
        
        if client_id not in self.usage:
            self.usage[client_id] = {
                "date": today,
                "messages": 0,
                "tokens": 0
            }
        
        client_usage = self.usage[client_id]
        
        if client_usage["date"] != today:
            client_usage["date"] = today
            client_usage["messages"] = 0
            client_usage["tokens"] = 0
        
        if client_usage["messages"] >= self.daily_limit_messages:
            return False, f"Daily message limit reached ({self.daily_limit_messages})"
        
        if client_usage["tokens"] >= self.daily_limit_tokens:
            return False, f"Daily token limit reached ({self.daily_limit_tokens})"
        
        return True, ""
    
    def record_usage(self, client_id: str, tokens: int):
        if client_id in self.usage:
            self.usage[client_id]["messages"] += 1
            self.usage[client_id]["tokens"] += tokens


class ZordEngine:
    """Simple wrapper for Zord model"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.model = None
        self.loaded = False
    
    def load_model(self) -> bool:
        if not LLAMA_AVAILABLE:
            print("llama-cpp-python not available")
            return False
        
        model_path = self.config.model_path
        
        if not os.path.exists(model_path):
            print(f"Model not found at: {model_path}")
            return False
        
        try:
            print(f"Loading model from: {model_path}")
            self.model = Llama(
                model_path=model_path,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
                verbose=False
            )
            self.loaded = True
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def format_prompt(self, user_input: str) -> str:
        return f"### Instruction:\n{user_input}\n\n### Response:\n"
    
    def generate(self, prompt: str, temperature: float = 0.7, 
                 max_tokens: int = 2048) -> Dict[str, Any]:
        if not self.loaded or not self.model:
            return {
                "response": "Model not loaded. Please wait and try again.",
                "tokens_generated": 0,
                "error": "Model not loaded"
            }
        
        try:
            formatted_prompt = self.format_prompt(prompt)
            
            output = self.model(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["### Instruction:", "### End", "\n\n\n"],
                echo=False
            )
            
            response = output["choices"][0]["text"].strip()
            tokens = output.get("usage", {}).get("total_tokens", len(response.split()))
            
            return {
                "response": response,
                "tokens_generated": tokens,
                "model": "ZordCoder-v1"
            }
            
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "tokens_generated": 0,
                "error": str(e)
            }


class ZordHandler(BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    engine: Optional[ZordEngine] = None
    usage_tracker: UsageTracker = UsageTracker()
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.send_json(200, {
                "status": "ok",
                "message": "Zord Coder API v1 - HuggingFace Spaces",
                "model_loaded": self.engine.loaded if self.engine else False,
                "endpoints": {
                    "POST /generate": "Generate response",
                    "GET /health": "Health check"
                }
            })
        elif parsed.path == '/health':
            self.send_json(200, {
                "status": "ok",
                "model_loaded": self.engine.loaded if self.engine else False
            })
        else:
            self.send_json(404, {"error": "Not found"})
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/generate':
            self.handle_generate()
        else:
            self.send_json(404, {"error": "Not found"})
    
    def handle_generate(self):
        client_id = self.usage_tracker.get_client_id(self)
        
        can_proceed, error_msg = self.usage_tracker.check_limit(client_id)
        if not can_proceed:
            self.send_json(429, {"error": error_msg})
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_json(400, {"error": "Empty request body"})
            return
        
        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            prompt = data.get("prompt", "")
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens", 2048)
            
            if not prompt:
                self.send_json(400, {"error": "Prompt is required"})
                return
            
            result = self.engine.generate(prompt, temperature, max_tokens)
            
            self.usage_tracker.record_usage(client_id, result.get("tokens_generated", 0))
            
            self.send_json(200, result)
            
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON"})
        except Exception as e:
            self.send_json(500, {"error": str(e)})


def download_model():
    """Download model from HuggingFace Hub"""
    print("=" * 50)
    print("  Downloading Model from HuggingFace Hub")
    print("=" * 50)
    print(f"Repo: {MODEL_REPO}")
    print(f"File: {MODEL_FILE}")
    print(f"Target: {MODEL_PATH}")
    print()
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    if os.path.exists(MODEL_PATH):
        size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"Model already exists ({size_mb:.1f} MB)")
        return MODEL_PATH
    
    if not HF_AVAILABLE:
        print("Error: huggingface-hub not available")
        return None
    
    try:
        print("Downloading... (this may take a few minutes)")
        downloaded_path = hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MODEL_FILE,
            local_dir=os.path.dirname(MODEL_PATH),
            local_dir_use_symlinks=False,
        )
        
        if downloaded_path != MODEL_PATH:
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
            os.rename(downloaded_path, MODEL_PATH)
        
        print(f"Model downloaded successfully!")
        return MODEL_PATH
        
    except Exception as e:
        print(f"Download failed: {e}")
        return None


def main():
    """Main entry point for HuggingFace Spaces"""
    print("=" * 50)
    print("  Zord Coder v1 - HuggingFace Spaces")
    print("=" * 50)
    print()
    
    model_path = download_model()
    if not model_path:
        print("Warning: Could not download model. Starting in demo mode.")
    
    config = ServerConfig(
        host=HOST,
        port=PORT,
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=4,
    )
    
    print()
    print(f"Host: {config.host}:{config.port}")
    print(f"Model: {config.model_path}")
    print()
    
    engine = ZordEngine(config)
    if model_path:
        engine.load_model()
    ZordHandler.engine = engine
    
    server = HTTPServer((config.host, config.port), ZordHandler)
    
    print()
    print(f"Server running at http://{config.host}:{config.port}")
    print("Ready to accept requests!")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
