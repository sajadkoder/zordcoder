#!/usr/bin/env python3
"""
Zord Coder v1 - Beautiful CLI Interface
Features:
- ASCII art banner
- Syntax highlighting
- Streaming output
- Reasoning mode toggle
- Multi-language support

Author: Zord Coder Team
Version: 1.0.0
"""

import os
import sys
import time
import signal
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.style import Style
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich not installed. Install with: pip install rich")

try:
    from src.zord_core import ZordCore, ZordConfig, GenerationConfig
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


#===============================================================================
# Custom Theme
#===============================================================================

ZORD_THEME = Theme({
    "banner.cyan": "bold cyan",
    "banner.green": "bold green",
    "banner.yellow": "bold yellow",
    "user": "bold blue",
    "assistant": "bold green",
    "system": "bold yellow",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "blue",
    "code": "cyan",
    "reasoning": "dim cyan italic",
    "metrics": "dim",
})


#===============================================================================
# ASCII Art Banner
#===============================================================================

ZORD_BANNER = """
[bold cyan]
 ██████╗ ███████╗███████╗██╗     ██╗███╗   ██╗███████╗
██╔═══██╗██╔════╝██╔════╝██║     ██║████╗  ██║██╔════╝
██║   ██║█████╗  █████╗  ██║     ██║██╔██╗ ██║█████╗  
██║   ██║██╔══╝  ██╔══╝  ██║     ██║██║╚██╗██║██╔══╝  
╚██████╔╝██║     ██║     ███████╗██║██║ ╚████║███████╗
 ╚═════╝ ╚═╝     ╚═╝     ╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝
[bold yellow]version 1.0.0[/bold yellow]
"""

ZORD_BANNER_COMPACT = """
[bold cyan]╔══════════════════════════════════════════════════╗
║  ZORD CODER v1 - Ultimate Coding Assistant    ║
╚══════════════════════════════════════════════════╝[/bold cyan]
"""


#===============================================================================
# Console Wrapper
#===============================================================================

class ZordConsole:
    """Wrapper for rich console with custom styling"""
    
    def __init__(self):
        self.console = Console(theme=ZORD_THEME) if RICH_AVAILABLE else None
        self.use_rich = RICH_AVAILABLE
        
    def print(self, message: str, style: str = ""):
        if self.use_rich:
            self.console.print(message)
        else:
            # Strip rich markup for plain output
            import re
            clean = re.sub(r'\[/?[^\]]+\]', '', message)
            print(clean)
            
    def print_banner(self, compact: bool = False):
        banner = ZORD_BANNER_COMPACT if compact else ZORD_BANNER
        self.print(banner)
        
    def print_panel(self, content: str, title: str = "", style: str = ""):
        if self.use_rich:
            self.console.print(Panel(content, title=title, style=style, box=box.ROUNDED))
        else:
            print(f"=== {title} ===")
            print(content)
            
    def print_table(self, data: List[List[str]], headers: List[str] = None):
        if self.use_rich:
            table = Table(show_header=bool(headers), headers=headers, box=box.SIMPLE)
            for row in data:
                table.add_row(*row)
            self.console.print(table)
        else:
            for row in data:
                print(" | ".join(row))
                
    def print_code(self, code: str, language: str = "python"):
        if self.use_rich:
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            self.console.print(syntax)
        else:
            print(code)
            
    def print_markdown(self, md: str):
        if self.use_rich:
            self.console.print(Markdown(md))
        else:
            print(md)
            
    def input(self, prompt: str = "> ") -> str:
        if self.use_rich:
            return self.console.input(prompt)
        else:
            return input(prompt)
            
    def clear(self):
        if self.use_rich:
            self.console.clear()
        else:
            print("\033[2J\033[H", end="")


#===============================================================================
# Language Support
#===============================================================================

LANGUAGE_SUPPORT = {
    "python": {"name": "Python", "icon": "🐍", "extensions": [".py", ".pyw"]},
    "javascript": {"name": "JavaScript", "icon": "📜", "extensions": [".js", ".mjs"]},
    "typescript": {"name": "TypeScript", "icon": "📘", "extensions": [".ts", ".tsx"]},
    "java": {"name": "Java", "icon": "☕", "extensions": [".java"]},
    "cpp": {"name": "C++", "icon": "⚙️", "extensions": [".cpp", ".cc", ".hpp"]},
    "rust": {"name": "Rust", "icon": "🦀", "extensions": [".rs"]},
    "go": {"name": "Go", "icon": "🐹", "extensions": [".go"]},
    "bash": {"name": "Bash", "icon": "💻", "extensions": [".sh"]},
    "html": {"name": "HTML", "icon": "🌐", "extensions": [".html", ".htm"]},
    "css": {"name": "CSS", "icon": "🎨", "extensions": [".css"]},
    "sql": {"name": "SQL", "icon": "🗃️", "extensions": [".sql"]},
    "c": {"name": "C", "icon": "🔧", "extensions": [".c", ".h"]},
    "csharp": {"name": "C#", "icon": "🔷", "extensions": [".cs"]},
    "php": {"name": "PHP", "icon": "🐘", "extensions": [".php"]},
    "ruby": {"name": "Ruby", "icon": "💎", "extensions": [".rb"]},
    "swift": {"name": "Swift", "icon": "🍎", "extensions": [".swift"]},
    "kotlin": {"name": "Kotlin", "icon": "🟣", "extensions": [".kt", ".kts"]},
    "scala": {"name": "Scala", "icon": "🔶", "extensions": [".scala"]},
    "r": {"name": "R", "icon": "📊", "extensions": [".r"]},
    "perl": {"name": "Perl", "icon": "🐪", "extensions": [".pl"]},
}


def get_language_indicator(languages: List[str] = None) -> str:
    """Get a string showing supported languages"""
    if languages:
        icons = [LANGUAGE_SUPPORT.get(l, {}).get("icon", "📄") for l in languages]
        return " ".join(icons)
    return " ".join([info["icon"] for info in list(LANGUAGE_SUPPORT.values())[:8]])


#===============================================================================
# Main CLI Application
#===============================================================================

class ZordCLI:
    """
    Zord Coder CLI - Beautiful command-line interface
    """
    
    def __init__(self, config: Optional[ZordConfig] = None):
        self.config = config or ZordConfig()
        self.console = ZordConsole()
        self.engine: Optional[ZordCore] = None
        
        # Session state
        self.reasoning_mode = False
        self.streaming = True
        self.current_language = "python"
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C"""
        print("\n\n[yellow]Interrupted. Type 'exit' to quit or 'clear' to clear history.[/yellow]")
        
    def initialize(self) -> bool:
        """Initialize the CLI and load model"""
        self.console.print_banner()
        
        if not CORE_AVAILABLE:
            self.console.print("[error]Error: zord_core not found![/error]")
            self.console.print("[info]Make sure zord_core.py is in the src directory[/info]")
            return False
            
        # Create engine
        self.engine = ZordCore(self.config)
        
        # Load model
        self.console.print("\n[info]Loading model...[/info]")
        
        if not self.engine.load_model():
            self.console.print(f"\n[error]Failed to load model: {self.config.model_path}[/error]")
            self.console.print("\n[info]Please download a GGUF model and place it in:[/info]")
            self.console.print(f"  {self.config.model_path}")
            return False
            
        return True
        
    def show_welcome(self):
        """Show welcome message"""
        self.console.print("\n")
        
        # Create welcome panel
        welcome_text = f"""
[bold green]Welcome to Zord Coder v1![/bold green]

[cyan]The ultimate coding assistant for Termux[/cyan]

[yellow]Quick Commands:[/yellow]
  • [bold]clear[/bold] - Clear conversation history
  • [bold]reasoning[/bold] - Toggle reasoning mode
  • [bold]stream[/bold] - Toggle streaming mode
  • [bold]metrics[/bold] - Show performance metrics
  • [bold]history[/bold] - Show conversation history
  • [bold]language <lang>[/bold] - Set output language
  • [bold]help[/bold] - Show this help
  • [bold]exit[/bold] - Exit the program

[green]Supported Languages:[/green]
{get_language_indicator()}

[cyan]Type your coding question below...[/cyan]
"""
        self.console.print_panel(welcome_text, title="🎉 Welcome", style="green")
        
    def show_help(self):
        """Show help message"""
        help_text = """
[bold yellow]Zord Coder v1 - Command Reference[/bold yellow]

[bold cyan]General Commands:[/bold cyan]
  help          - Show this help message
  clear         - Clear conversation history
  exit, quit    - Exit the program

[bold cyan]Mode Commands:[/bold cyan]
  reasoning     - Toggle reasoning mode (Chain-of-thought)
  stream        - Toggle streaming output
  metrics       - Show performance metrics

[bold cyan]Settings Commands:[/bold cyan]
  language <lang> - Set preferred programming language
                   (python, javascript, rust, go, etc.)
  temp <value>    - Set temperature (0.0-1.0)
  max <tokens>   - Set max tokens (1-4096)

[bold cyan]Query Commands:[/bold cyan]
  history        - Show conversation history
  info           - Show model information

[bold cyan]Tips:[/bold cyan]
  • Ask specific, clear questions for better answers
  • Use reasoning mode for complex problems
  • Set your preferred language for targeted code
"""
        self.console.print_panel(help_text, title="📚 Help", style="blue")
        
    def show_metrics(self):
        """Show performance metrics"""
        if not self.engine:
            return
            
        metrics = self.engine.get_metrics()
        
        metrics_table = Table(title="📊 Performance Metrics", box=box.ROUNDED)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        metrics_table.add_row("Total Requests", str(metrics["total_requests"]))
        metrics_table.add_row("Total Tokens", str(metrics["total_tokens_generated"]))
        metrics_table.add_row("Avg Tokens/sec", f"{metrics['avg_tokens_per_second']:.2f}")
        metrics_table.add_row("Avg Response Time", f"{metrics['avg_response_time']:.2f}s")
        
        self.console.console.print(metrics_table)
        
    def show_info(self):
        """Show model information"""
        if not self.engine:
            return
            
        info = self.engine.get_model_info()
        
        if not info.get("loaded"):
            self.console.print("[error]No model loaded[/error]")
            return
            
        info_table = Table(title="ℹ️ Model Information", box=box.ROUNDED)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Status", "✓ Loaded")
        info_table.add_row("Model", os.path.basename(info.get("model_path", "N/A")))
        info_table.add_row("Context Length", str(info.get("n_ctx", "N/A")))
        info_table.add_row("Threads", str(info.get("n_threads", "N/A")))
        
        self.console.console.print(info_table)
        
    def handle_command(self, user_input: str) -> bool:
        """
        Handle special commands
        
        Returns:
            True if command was handled, False if regular input
        """
        cmd = user_input.strip().lower()
        
        if cmd in ["exit", "quit", "q"]:
            self.console.print("[yellow]Goodbye! Happy coding! 👋[/yellow]")
            return True
            
        elif cmd == "clear":
            if self.engine:
                self.engine.clear_history()
            self.console.print("[green]✓ Conversation history cleared[/green]")
            return True
            
        elif cmd == "help" or cmd == "?":
            self.show_help()
            return True
            
        elif cmd == "reasoning":
            self.reasoning_mode = not self.reasoning_mode
            status = "✓ Enabled" if self.reasoning_mode else "✗ Disabled"
            self.console.print(f"[cyan]Reasoning mode: {status}[/cyan]")
            if self.reasoning_mode:
                self.console.print("[dim]Chain-of-thought enabled - expect more detailed reasoning[/dim]")
            return True
            
        elif cmd == "stream":
            self.streaming = not self.streaming
            status = "✓ Enabled" if self.streaming else "✗ Disabled"
            self.console.print(f"[cyan]Streaming mode: {status}[/cyan]")
            return True
            
        elif cmd == "metrics":
            self.show_metrics()
            return True
            
        elif cmd == "history":
            if self.engine:
                history = self.engine.get_history()
                if history:
                    self.console.print(f"\n[cyan]Conversation History ({len(history)} messages):[/cyan]\n")
                    for i, msg in enumerate(history[-10:]):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")[:100]
                        if role == "user":
                            self.console.print(f"  [blue]You:[/blue] {content}...")
                        else:
                            self.console.print(f"  [green]Zord:[/green] {content}...")
                else:
                    self.console.print("[yellow]No conversation history[/yellow]")
            return True
            
        elif cmd == "info":
            self.show_info()
            return True
            
        elif cmd.startswith("language "):
            lang = cmd.split(" ", 1)[1].strip()
            if lang in LANGUAGE_SUPPORT:
                self.current_language = lang
                self.console.print(f"[green]✓ Preferred language set to: {LANGUAGE_SUPPORT[lang]['name']} {LANGUAGE_SUPPORT[lang]['icon']}[/green]")
            else:
                self.console.print(f"[yellow]Unknown language: {lang}[/yellow]")
                self.console.print(f"[info]Available: {', '.join(LANGUAGE_SUPPORT.keys())}[/info]")
            return True
            
        elif cmd.startswith("temp "):
            try:
                temp = float(cmd.split(" ", 1)[1])
                self.console.print(f"[green]✓ Temperature set to: {temp}[/green]")
            except:
                self.console.print("[error]Invalid temperature value[/error]")
            return True
            
        elif cmd.startswith("max "):
            try:
                max_tok = int(cmd.split(" ", 1)[1])
                self.console.print(f"[green]✓ Max tokens set to: {max_tok}[/green]")
            except:
                self.console.print("[error]Invalid max tokens value[/error]")
            return True
            
        return False
        
    def format_response(self, response: str) -> str:
        """Format response with code highlighting"""
        import re
        
        # Check for code blocks
        code_block_pattern = r'```(\w+)?\n(.*?)```'
        
        def replace_code_block(match):
            language = match.group(1) or "python"
            code = match.group(2)
            return f"\n\n{code}\n\n"  # Will be syntax highlighted later
            
        formatted = re.sub(code_block_pattern, replace_code_block, response, flags=re.DOTALL)
        
        return formatted
        
    def print_streaming_response(self, response: str, language: str = None):
        """Print response with streaming effect and syntax highlighting"""
        if not RICH_AVAILABLE:
            print(response)
            return
            
        # Detect and print code blocks
        import re
        parts = re.split(r'(```[\w]*\n[\s\S]*?```)', response)
        
        for part in parts:
            if part.startswith('```'):
                # Code block
                match = re.match(r'```(\w+)?\n([\s\S]*?)```', part)
                if match:
                    code_lang = match.group(1) or language or "python"
                    code = match.group(2).rstrip()
                    self.console.console.print("\n")
                    self.console.print_code(code, code_lang)
                    self.console.console.print("\n")
            else:
                # Regular text
                if part.strip():
                    self.console.console.print(part, end="")
                    
        print()  # Newline after response
        
    def run(self):
        """Run the main CLI loop"""
        # Initialize
        if not self.initialize():
            return
            
        # Show welcome
        self.show_welcome()
        
        # Main loop
        while True:
            try:
                # Get user input
                user_input = self.console.input("\n[bold blue]You:[/bold blue] ")
                
                if not user_input.strip():
                    continue
                    
                # Handle commands
                if self.handle_command(user_input):
                    continue
                    
                # Generate response
                if not self.engine:
                    self.console.print("[error]Engine not initialized[/error]")
                    continue
                    
                # Configure generation
                gen_config = GenerationConfig(
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    repeat_penalty=1.1,
                    stream=self.streaming,
                )
                
                # Add reasoning prefix if enabled
                if self.reasoning_mode:
                    user_input = f"Let me think through this step by step:\n\n{user_input}"
                    
                # Show thinking indicator
                if not self.streaming:
                    with self.console.console.status("[bold green]Zord is thinking...[/bold green]"):
                        response, metrics = self.engine.generate_response(user_input, gen_config)
                    self.console.print("\n")
                    self.console.print("[bold green]Zord:[/bold green]")
                    self.print_streaming_response(response, self.current_language)
                else:
                    # Streaming mode
                    self.console.print("\n[bold green]Zord:[/bold green] ", end="")
                    
                    full_response = ""
                    for token, token_metrics in self.engine.stream_response(user_input, gen_config):
                        # Check for code blocks
                        import re
                        if re.match(r'```', token):
                            print()  # Newline before code block
                        print(token, end="")
                        full_response += token
                        
                    print()  # Newline after response
                    
                    # Update metrics
                    metrics = self.engine.get_metrics()
                    
                # Show quick metrics
                if RICH_AVAILABLE:
                    self.console.console.print(f"\n[dim]⏱ {metrics.get('generation_time', 0):.1f}s | 💬 {metrics.get('tokens_generated', 0)} tokens | ⚡ {metrics.get('tokens_per_second', 0):.1f} tok/s[/dim]")
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue
                
            except Exception as e:
                self.console.print(f"[error]Error: {e}[/error]")
                import traceback
                traceback.print_exc()
                
        # Cleanup
        if self.engine:
            self.engine.unload_model()


#===============================================================================
# Command Line Interface
#===============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Zord Coder v1 - Ultimate Termux Coding Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to generate response for (if not interactive)"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=os.getenv("ZORD_MODEL_PATH", "models/zordcoder-v1-q4_k_m.gguf"),
        help="Path to GGUF model file"
    )
    
    parser.add_argument(
        "--context", "-c",
        type=int,
        default=2048,
        help="Context length (default: 2048)"
    )
    
    parser.add_argument(
        "--threads", "-t",
        type=int,
        default=4,
        help="Number of CPU threads (default: 4)"
    )
    
    parser.add_argument(
        "--temperature", "--temp",
        type=float,
        default=0.1,
        help="Generation temperature (default: 0.1)"
    )
    
    parser.add_argument(
        "--max-tokens", "--max",
        type=int,
        default=1024,
        help="Maximum tokens to generate (default: 1024)"
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming output"
    )
    
    parser.add_argument(
        "--reasoning",
        action="store_true",
        help="Enable reasoning mode (Chain-of-thought)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start in interactive mode"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show model information and exit"
    )
    
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Show performance metrics and exit"
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create console
    console = ZordConsole()
    console.print_banner()
    
    # Create configuration
    config = ZordConfig(
        model_path=args.model,
        n_ctx=args.context,
        n_threads=args.threads,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    
    # Create CLI
    cli = ZordCLI(config)
    
    # Handle info/metrics flags
    if args.info or args.metrics:
        if cli.initialize():
            if args.info:
                cli.show_info()
            if args.metrics:
                cli.show_metrics()
        return 0
        
    # Interactive or single prompt mode
    if args.interactive or args.prompt is None:
        # Interactive mode
        cli.run()
    else:
        # Single prompt mode
        console.print("\n[info]Loading model...[/info]\n")
        
        if not cli.initialize():
            return 1
            
        # Generate response
        gen_config = GenerationConfig(
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            stream=not args.no_stream,
        )
        
        if args.reasoning:
            args.prompt = f"Let me think through this step by step:\n\n{args.prompt}"
            
        if args.no_stream:
            response, metrics = cli.engine.generate_response(args.prompt, gen_config)
            console.print(f"\n[bold green]Response:[/bold green]\n{response}\n")
        else:
            console.print(f"\n[bold green]Zord:[/bold green] ")
            for token, metrics in cli.engine.stream_response(args.prompt, gen_config):
                print(token, end="")
            print()
            
        # Show metrics
        if RICH_AVAILABLE:
            metrics = cli.engine.get_metrics()
            console.console.print(f"\n[dim]⏱ {metrics.get('generation_time', 0):.1f}s | 💬 {metrics.get('tokens_generated', 0)} tokens | ⚡ {metrics.get('tokens_per_second', 0):.1f} tok/s[/dim]")
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
