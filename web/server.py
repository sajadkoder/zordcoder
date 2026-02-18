#!/usr/bin/env python3
"""
Zord Coder v1 - Simple API Server
Provides HTTP API for Next.js frontend

Usage:
    python server.py
    # Runs on http://localhost:8000
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Simple HTTP server using built-in http.server
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("Warning: llama-cpp-python not installed")


#===============================================================================
# Configuration
#===============================================================================

@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    model_path: str = "models/zordcoder-v1-q4_k_m.gguf"
    n_ctx: int = 2048
    n_threads: int = 4
    n_gpu_layers: int = 0


#===============================================================================
# Usage Tracking
#===============================================================================

class UsageTracker:
    """Track API usage per client"""
    
    def __init__(self):
        self.usage: Dict[str, Dict[str, Any]] = {}
        self.daily_limit_messages = 50
        self.daily_limit_tokens = 50000
    
    def get_client_id(self, handler) -> str:
        """Get unique client ID from request"""
        client = handler.client_address[0]
        return f"{client}"
    
    def check_limit(self, client_id: str) -> tuple[bool, str]:
        """Check if client has reached limit"""
        today = datetime.now().date().isoformat()
        
        if client_id not in self.usage:
            self.usage[client_id] = {
                "date": today,
                "messages": 0,
                "tokens": 0
            }
        
        client_usage = self.usage[client_id]
        
        # Reset if new day
        if client_usage["date"] != today:
            client_usage["date"] = today
            client_usage["messages"] = 0
            client_usage["tokens"] = 0
        
        # Check limits
        if client_usage["messages"] >= self.daily_limit_messages:
            return False, f"Daily message limit reached ({self.daily_limit_messages})"
        
        if client_usage["tokens"] >= self.daily_limit_tokens:
            return False, f"Daily token limit reached ({self.daily_limit_tokens})"
        
        return True, ""
    
    def record_usage(self, client_id: str, tokens: int):
        """Record API usage"""
        if client_id in self.usage:
            self.usage[client_id]["messages"] += 1
            self.usage[client_id]["tokens"] += tokens


#===============================================================================
# Zord Engine
#===============================================================================

class ZordEngine:
    """Simple wrapper for Zord model"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.model = None
        self.loaded = False
    
    def load_model(self) -> bool:
        """Load the model"""
        if not LLAMA_AVAILABLE:
            print("llama-cpp-python not available")
            return False
        
        model_path = self.config.model_path
        
        # Try multiple paths
        possible_paths = [
            model_path,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), model_path),
            os.path.join(os.getcwd(), model_path),
        ]
        
        actual_path = None
        for path in possible_paths:
            if os.path.exists(path):
                actual_path = path
                break
        
        if not actual_path:
            print(f"Model not found at: {model_path}")
            return False
        
        try:
            print(f"Loading model from: {actual_path}")
            self.model = Llama(
                model_path=actual_path,
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
    
    def generate(self, prompt: str, temperature: float = 0.7, 
                 max_tokens: int = 2048) -> Dict[str, Any]:
        """Generate response"""
        if not self.loaded or not self.model:
            return {
                "response": "Model not loaded. Please start the server with model loaded.",
                "tokens_generated": 0,
                "error": "Model not loaded"
            }
        
        try:
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|endoftext|>", "<|eot_id|>"],
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


#===============================================================================
# HTTP Handler
#===============================================================================

class ZordHandler(BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    engine: Optional[ZordEngine] = None
    usage_tracker: UsageTracker = UsageTracker()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def send_json(self, status: int, data: dict):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.send_json(200, {
                "status": "ok",
                "message": "Zord Coder API v1",
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
        """Handle POST requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/generate':
            self.handle_generate()
        else:
            self.send_json(404, {"error": "Not found"})
    
    def handle_generate(self):
        """Handle generate request"""
        # Get client ID
        client_id = self.usage_tracker.get_client_id(self)
        
        # Check limits
        can_proceed, error_msg = self.usage_tracker.check_limit(client_id)
        if not can_proceed:
            self.send_json(429, {"error": error_msg})
            return
        
        # Read request body
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
            
            # Generate
            result = self.engine.generate(prompt, temperature, max_tokens)
            
            # Record usage
            self.usage_tracker.record_usage(client_id, result.get("tokens_generated", 0))
            
            # Send response
            self.send_json(200, result)
            
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON"})
        except Exception as e:
            self.send_json(500, {"error": str(e)})


#===============================================================================
# Main Server
#===============================================================================

def main():
    """Start the server"""
    config = ServerConfig()
    
    print("=" * 50)
    print("  Zord Coder API Server")
    print("=" * 50)
    print(f"Host: {config.host}:{config.port}")
    print(f"Model: {config.model_path}")
    print()
    
    # Try to load model
    if LLAMA_AVAILABLE:
        print("Loading model...")
        engine = ZordEngine(config)
        if engine.load_model():
            print("Model loaded!")
        else:
            print("Warning: Model not loaded. Running in demo mode.")
        ZordHandler.engine = engine
    else:
        print("llama-cpp-python not available. Running in demo mode.")
        ZordHandler.engine = None
    
    # Start server
    server = HTTPServer((config.host, config.port), ZordHandler)
    
    print()
    print(f"Server running at http://{config.host}:{config.port}")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
