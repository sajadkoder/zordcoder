#!/usr/bin/env python3
"""
Zord Coder v1 - Core Inference Engine
Handles model loading, grammar sampling, and streaming generation

Author: Zord Coder Team
Version: 1.0.0
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Callable, Generator, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

try:
    from llama_cpp import Llama
    from llama_cpp.llama_chat_format import Llama3ChatTemplateHandler
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. Install with: pip install llama-cpp-python")

try:
    from rich.console import Console
    from rich.theme import Theme
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


#===============================================================================
# Configuration
#===============================================================================

class GenerationMode(Enum):
    """Generation mode options"""
    DEFAULT = "default"
    REASONING = "reasoning"  # Chain-of-thought like DeepSeek-R1
    CREATIVE = "creative"
    PRECISE = "precise"


@dataclass
class GenerationConfig:
    """Configuration for text generation"""
    max_tokens: int = 2048
    temperature: float = 0.1
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = True
    stop: List[str] = field(default_factory=lambda: ["<|endoftext|>", "<|eot_id|>"])
    
    # Reasoning mode settings
    reasoning_mode: bool = False
    reasoning_max_tokens: int = 1024
    
    # Performance settings
    n_threads: int = 4
    n_gpu_layers: int = 0
    n_batch: int = 512
    context_overlap: int = 0


@dataclass
class ZordConfig:
    """Main configuration for Zord Coder"""
    # Model
    model_path: str = field(default_factory=lambda: os.getenv("ZORD_MODEL_PATH", "models/zordcoder-v1-q4_k_m.gguf"))
    model_type: str = "llama"
    
    # Context
    n_ctx: int = 2048
    n_keep: int = 0
    
    # Performance
    n_threads: int = field(default_factory=lambda: int(os.getenv("ZORD_N_THREADS", "4")))
    n_gpu_layers: int = field(default_factory=lambda: int(os.getenv("ZORD_N_GPU_LAYERS", "0")))
    n_batch: int = field(default_factory=lambda: int(os.getenv("ZORD_N_BATCH", "512")))
    
    # Cache
    cache_dir: Optional[str] = field(default_factory=lambda: os.getenv("ZORD_CACHE_DIR"))
    kv_cache_quantization: bool = True
    
    # Verbose
    verbose: bool = False
    log_level: str = "INFO"
    
    # Generation defaults
    temperature: float = 0.1
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 2048
    repeat_penalty: float = 1.1
    
    # Paths
    logs_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "..", "logs"))


#===============================================================================
# Custom Themes for Rich
#===============================================================================

if RICH_AVAILABLE:
    ZORD_THEME = Theme({
        "zord.banner": "cyan bold",
        "zord.title": "bold cyan",
        "zord.subtitle": "green",
        "zord.user": "blue bold",
        "zord.assistant": "green bold",
        "zord.system": "yellow bold",
        "zord.error": "red bold",
        "zord.warning": "yellow bold",
        "zord.info": "blue",
        "zord.code": "cyan",
        "zord.reasoning": "dim cyan italic",
    })


#===============================================================================
# Inference Engine
#===============================================================================

class ZordCore:
    """
    Core inference engine for Zord Coder v1
    
    Handles:
    - Model loading and caching
    - Text generation with streaming
    - Grammar-based sampling
    - Performance optimization
    - Multi-language detection
    """
    
    def __init__(self, config: Optional[ZordConfig] = None):
        self.config = config or ZordConfig()
        self.llm: Optional[Llama] = None
        self.console = Console(theme=ZORD_THEME) if RICH_AVAILABLE else None
        self.conversation_history: List[Dict] = []
        self.is_loaded = False
        
        # Setup logging
        self._setup_logging()
        
        # Performance metrics
        self.metrics = {
            "total_tokens_generated": 0,
            "total_requests": 0,
            "avg_tokens_per_second": 0.0,
            "avg_response_time": 0.0,
        }
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(self.config.logs_dir, "zord_core.log"))
            ] if self.config.logs_dir else []
        )
        self.logger = logging.getLogger("ZordCore")
        
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load the GGUF model into memory
        
        Args:
            model_path: Path to the GGUF model file
            
        Returns:
            True if model loaded successfully
        """
        model_path = model_path or self.config.model_path
        
        if not os.path.exists(model_path):
            self.logger.error(f"Model file not found: {model_path}")
            if self.console:
                self.console.print(f"[zord.error]Error: Model file not found: {model_path}")
            return False
            
        if not LLAMA_CPP_AVAILABLE:
            self.logger.error("llama-cpp-python not installed")
            return False
            
        try:
            self.logger.info(f"Loading model from {model_path}")
            
            if self.console:
                self.console.print(f"[zord.info]Loading model: {os.path.basename(model_path)}")
            
            self.llm = Llama(
                model_path=model_path,
                n_ctx=self.config.n_ctx,
                n_keep=self.config.n_keep,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
                n_batch=self.config.n_batch,
                kv_cache_quantization=self.config.kv_cache_quantization,
                verbose=self.config.verbose,
            )
            
            self.is_loaded = True
            self.logger.info("Model loaded successfully")
            
            if self.console:
                self.console.print("[zord.assistant]✓ Model loaded successfully!")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            if self.console:
                self.console.print(f"[zord.error]Failed to load model: {e}")
            return False
            
    def unload_model(self):
        """Unload model from memory"""
        if self.llm:
            del self.llm
            self.llm = None
            self.is_loaded = False
            
            # Force garbage collection
            import gc
            gc.collect()
            
            self.logger.info("Model unloaded")
            
    def create_system_prompt(self) -> str:
        """
        Create the system prompt that defines Zord Coder's identity
        
        Returns:
            System prompt string
        """
        return """You are Zord Coder version 1, an advanced, lightweight, and blazing-fast AI coding assistant optimized for mobile devices.

Your core capabilities:
- Provide accurate, efficient code in Python, JavaScript, TypeScript, C++, Rust, Go, Java, Bash, and more
- Explain code concepts clearly and concisely
- Suggest best practices and modern patterns
- Help debug and optimize code
- Answer programming questions

Your characteristics:
- SPEED: You provide fast, responsive answers
- ACCURACY: You write correct, well-tested code
- CLARITY: You explain complex concepts simply
- CONCISENESS: You avoid unnecessary verbosity
- BEST PRACTICES: You follow modern coding standards

When responding:
1. Provide direct, executable code solutions
2. Use proper syntax highlighting
3. Include brief explanations when helpful
4. Suggest optimizations and alternatives
5. Handle errors gracefully

You identify yourself as "Zord Coder v1" when asked.
"""
        
    def format_prompt(self, user_input: str, include_history: bool = True) -> str:
        """
        Format the prompt with conversation history
        
        Args:
            user_input: The user's input
            include_history: Whether to include conversation history
            
        Returns:
            Formatted prompt string
        """
        system_prompt = self.create_system_prompt()
        
        # Build conversation history
        history_text = ""
        if include_history and self.conversation_history:
            for entry in self.conversation_history[-8:]:  # Keep last 8 exchanges
                if entry.get("role") == "user":
                    history_text += f"<|start_header_id|>user<|end_header_id|>\n\n{entry.get('content', '')}<|eot_id|>\n"
                elif entry.get("role") == "assistant":
                    history_text += f"<|start_header_id|>assistant<|end_header_id|>\n\n{entry.get('content', '')}<|eot_id|>\n"
        
        # Create full prompt (Llama 3 format)
        full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>\n{history_text}<|start_header_id|>user<|end_header_id|>\n\n{user_input}<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        return full_prompt
        
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[str, Dict[str, float]]:
        """
        Generate text from prompt
        
        Args:
            prompt: The input prompt
            config: Generation configuration
            callback: Optional callback for streaming (receives tokens)
            
        Returns:
            Tuple of (generated_text, metrics_dict)
        """
        if not self.is_loaded or self.llm is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        config = config or GenerationConfig()
        
        start_time = time.time()
        
        # Build generation kwargs
        gen_kwargs = {
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "top_k": config.top_k,
            "repeat_penalty": config.repeat_penalty,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
            "stop": config.stop,
            "echo": False,
            "stream": config.stream,
        }
        
        generated_text = ""
        
        try:
            if config.stream and callback:
                # Streaming generation with callback
                stream_response = self.llm(prompt, **gen_kwargs)
                
                for token_info in stream_response:
                    token = token_info["choices"][0]["text"]
                    generated_text += token
                    callback(token)
                    
            else:
                # Non-streaming generation
                response = self.llm(prompt, **gen_kwargs)
                generated_text = response["choices"][0]["text"].strip()
                
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            raise
            
        # Calculate metrics
        generation_time = time.time() - start_time
        tokens_generated = len(generated_text.split())
        tokens_per_second = tokens_generated / generation_time if generation_time > 0 else 0
        
        metrics = {
            "generation_time": generation_time,
            "tokens_generated": tokens_generated,
            "tokens_per_second": tokens_per_second,
            "total_tokens": tokens_generated,
        }
        
        # Update internal metrics
        self._update_metrics(tokens_generated, generation_time)
        
        return generated_text, metrics
        
    def generate_response(
        self,
        user_input: str,
        config: Optional[GenerationConfig] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[str, Dict[str, float]]:
        """
        Generate a response to user input, including conversation history
        
        Args:
            user_input: The user's message
            config: Generation configuration
            stream_callback: Optional callback for streaming
            
        Returns:
            Tuple of (response_text, metrics_dict)
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Format prompt
        prompt = self.format_prompt(user_input)
        
        # Generate response
        response, metrics = self.generate(prompt, config, stream_callback)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        })
        
        return response, metrics
        
    def stream_response(
        self,
        user_input: str,
        config: Optional[GenerationConfig] = None
    ) -> Generator[Tuple[str, Dict[str, float]], None, None]:
        """
        Stream response as a generator
        
        Args:
            user_input: The user's message
            config: Generation configuration
            
        Yields:
            Tuple of (token, metrics) for each token
        """
        config = config or GenerationConfig()
        
        prompt = self.format_prompt(user_input)
        
        gen_kwargs = {
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "top_k": config.top_k,
            "repeat_penalty": config.repeat_penalty,
            "stop": config.stop,
            "echo": False,
            "stream": True,
        }
        
        start_time = time.time()
        generated_text = ""
        tokens_generated = 0
        
        try:
            for token_info in self.llm(prompt, **gen_kwargs):
                token = token_info["choices"][0]["text"]
                generated_text += token
                tokens_generated += 1
                
                # Calculate running metrics
                elapsed = time.time() - start_time
                tokens_per_second = tokens_generated / elapsed if elapsed > 0 else 0
                
                metrics = {
                    "tokens_generated": tokens_generated,
                    "tokens_per_second": tokens_per_second,
                    "generation_time": elapsed,
                }
                
                yield token, metrics
                
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            raise
            
    def _update_metrics(self, tokens: int, time_taken: float):
        """Update internal performance metrics"""
        self.metrics["total_tokens_generated"] += tokens
        self.metrics["total_requests"] += 1
        
        # Running average
        total = self.metrics["total_requests"]
        prev_avg_tps = self.metrics["avg_tokens_per_second"]
        prev_avg_rt = self.metrics["avg_response_time"]
        
        current_tps = tokens / time_taken if time_taken > 0 else 0
        
        self.metrics["avg_tokens_per_second"] = (prev_avg_tps * (total - 1) + current_tps) / total
        self.metrics["avg_response_time"] = (prev_avg_rt * (total - 1) + time_taken) / total
        
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        return self.metrics.copy()
        
    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = {
            "total_tokens_generated": 0,
            "total_requests": 0,
            "avg_tokens_per_second": 0.0,
            "avg_response_time": 0.0,
        }
        
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()
        
    #=========================================================================
    # Utility Methods
    #=========================================================================
    
    def detect_language(self, code: str) -> str:
        """
        Auto-detect programming language from code content
        
        Args:
            code: Source code string
            
        Returns:
            Detected language name
        """
        language_indicators = {
            "python": [
                "def ", "import ", "from ", "class ", "print(",
                "if __name__", "__init__", "self.", "elif ", "except:"
            ],
            "javascript": [
                "function ", "const ", "let ", "var ", "=>",
                "console.log", "require(", "module.exports", "async "
            ],
            "typescript": [
                "interface ", "type ", ": string", ": number",
                "private ", "public ", "readonly ", "import type"
            ],
            "java": [
                "public class", "private void", "public static void",
                "System.out.println", "import java.", "@Override"
            ],
            "cpp": [
                "#include", "std::", "int main(", "cout <<", "endl",
                "namespace ", "template<", "::"
            ],
            "rust": [
                "fn ", "let mut", "impl ", "pub fn", "use ",
                "println!", "match ", "Some(", "None", "Ok(", "Err("
            ],
            "go": [
                "package main", "func main()", "import (",
                "fmt.", "go func", "defer ", "chan ", "interface{}"
            ],
            "bash": [
                "#!/bin/bash", "echo ", "if [", "fi",
                "export ", "source ", "chmod ", "awk ", "sed "
            ],
            "html": [
                "<html", "<div", "<span", "<p>",
                "<!DOCTYPE", "class=", "id="
            ],
            "css": [
                "{", "}", ":", ";", "color:",
                "background-", "margin:", "padding:", "@media"
            ],
            "sql": [
                "SELECT ", "FROM ", "WHERE ", "INSERT ",
                "UPDATE ", "DELETE ", "JOIN ", "CREATE TABLE"
            ],
        }
        
        code_lower = code.lower()
        scores = {}
        
        for lang, indicators in language_indicators.items():
            score = sum(1 for ind in indicators if ind in code_lower)
            scores[lang] = score
            
        if not scores or max(scores.values()) == 0:
            return "text"
            
        return max(scores, key=scores.get)
        
    def format_code_block(self, code: str, language: Optional[str] = None) -> str:
        """
        Format code with markdown code blocks
        
        Args:
            code: Source code
            language: Optional language hint
            
        Returns:
            Formatted markdown string
        """
        if language is None:
            language = self.detect_language(code)
            
        return f"```{language}\n{code}\n```"
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_loaded or self.llm is None:
            return {"loaded": False}
            
        return {
            "loaded": True,
            "model_path": self.config.model_path,
            "n_ctx": self.config.n_ctx,
            "n_threads": self.config.n_threads,
            "n_gpu_layers": self.config.n_gpu_layers,
            "metrics": self.metrics,
        }


#===============================================================================
# Grammar-Based Generation
#===============================================================================

class ZordGrammar:
    """
    Grammar-based generation for structured outputs
    Supports JSON, XML, and custom grammars
    """
    
    @staticmethod
    def json_grammar() -> str:
        """Get JSON grammar constraint"""
        return '''
json ::= object | array
object ::= "{" "}" | "{" members "}"
members ::= pair | pair "," members
pair ::= string ":" value
array ::= "[" "]" | "[" elements "]"
elements ::= value | value "," elements
value ::= string | number | object | array | "true" | "false" | "null"
string ::= '"' characters '"'
characters ::= "" | character characters
character ::= [^"\\] | "\\" escape
escape ::= '"' | "\\" | "/" | "b" | "f" | "n" | "r" | "t" | "u" hex hex hex hex
hex ::= [0-9A-Fa-f]
number ::= int | int frac | int exp | int frac exp
int ::= digit | digit1-9 digits | "-" digit | "-" digit1-9 digits
frac ::= "." digits
exp ::= e digits
digits ::= digit | digit digits
digit ::= [0-9]
digit1-9 ::= [1-9]
e ::= "e" | "e+" | "e-" | "E" | "E+" | "E-"
'''
    
    @staticmethod
    def code_block_grammar() -> str:
        """Get code block grammar"""
        return '''
code ::= language? NL body NL
language ::= "python" | "javascript" | "typescript" | "java" | "cpp" | "rust" | "go" | "bash" | "html" | "css" | "sql"
body ::= (line | indented)+
line ::= (char - NL) NL
indented ::= "    " line
char ::= ANY - NL
NL ::= "\\n"
'''


#===============================================================================
# Main Entry Point
#===============================================================================

def main():
    """Test the inference engine"""
    print("Zord Coder v1 - Core Inference Engine")
    print("=" * 50)
    
    # Load configuration
    config = ZordConfig()
    
    # Check if model exists
    if not os.path.exists(config.model_path):
        print(f"\nError: Model file not found at {config.model_path}")
        print("\nPlease download a GGUF model first.")
        print("Recommended: https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF")
        return 1
        
    # Create engine
    engine = ZordCore(config)
    
    # Load model
    if not engine.load_model():
        print("\nFailed to load model")
        return 1
        
    # Test generation
    print("\nTesting generation...")
    response, metrics = engine.generate_response(
        "Write a Python function to calculate factorial"
    )
    
    print(f"\nResponse: {response[:200]}...")
    print(f"\nMetrics:")
    print(f"  Tokens: {metrics['tokens_generated']}")
    print(f"  Time: {metrics['generation_time']:.2f}s")
    print(f"  Speed: {metrics['tokens_per_second']:.1f} tokens/sec")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
