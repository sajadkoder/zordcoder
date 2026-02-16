#!/bin/bash
#===============================================================================
# Zord Coder v1 - Termux Setup Script
# Installs all dependencies for running Zord Coder on Android/Termux
#
# Usage:
#   bash setup_termux.sh
#
# Author: Zord Coder Team
# Version: 1.0.0
#===============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ZORD_DIR="$HOME/zordcoder"
MODEL_DIR="$ZORD_DIR/models"
CACHE_DIR="$ZORD_DIR/cache"
LOG_DIR="$ZORD_DIR/logs"

#===============================================================================
# Helper Functions
#===============================================================================

print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
 ██████╗ ███████╗███████╗██╗     ██╗███╗   ██╗███████╗
██╔═══██╗██╔════╝██╔════╝██║     ██║████╗  ██║██╔════╝
██║   ██║█████╗  █████╗  ██║     ██║██╔██╗ ██║█████╗  
██║   ██║██╔══╝  ██╔══╝  ██║     ██║██║╚██╗██║██╔══╝  
╚██████╔╝██║     ██║     ███████╗██║██║ ╚████║███████╗
 ╚═════╝ ╚═╝     ╚═╝     ╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝
                                                     
          ██████╗ ███████╗ █████╗ ██████╗ 
          ██╔══██╗██╔════╝██╔══██╗██╔══██╗
          ██████╔╝█████╗  ███████║██║  ██║
          ██╔══██╗██╔══╝  ██╔══██║██║  ██║
          ██║  ██║███████╗██║  ██║██████╔╝
          ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ 
                                                      
    ██████╗ ███████╗██╗   ██╗
    ██╔══██╗██╔════╝██║   ██║
    ██║  ██║█████╗  ██║   ██║
    ██║  ██║██╔══╝  ╚██╗ ██╔╝
    ██████╔╝███████╗ ╚████╔╝ 
    ╚═════╝ ╚══════╝  ╚═══╝  
    
    ███████╗██████╗ ███████╗ █████╗  ██████╗██╗  ██╗
    ██╔════╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║
    █████╗  ██████╔╝█████╗  ███████║██║     ███████║
    ██╔══╝  ██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║
    ███████╗██║  ██║███████╗██║  ██║╚██████╗██║  ██║
    ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
EOF
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

#===============================================================================
# Environment Check
#===============================================================================

check_environment() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                    ENVIRONMENT CHECK                        ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    # Check if running in Termux
    if [ ! -d "/data/data/com.termux" ] && [ ! -f "/usr/bin/apt" ]; then
        print_warning "This script is designed for Termux on Android."
        print_warning "Running on: $(uname -s)"
    fi
    
    # Check OS
    print_info "Operating System: $(uname -s)"
    print_info "Architecture: $(uname -m)"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_status "Python: $PYTHON_VERSION"
    else
        print_error "Python not found!"
        exit 1
    fi
    
    # Check available storage
    STORAGE=$(df -h "$HOME" | tail -1 | awk '{print $3 " available"}')
    print_info "Storage: $STORAGE"
    
    # Check RAM
    if [ -f /proc/meminfo ]; then
        RAM=$(free -h | grep Mem | awk '{print $2 " total"}')
        print_info "RAM: $RAM"
    fi
}

#===============================================================================
# System Update
#===============================================================================

update_system() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                    UPDATING SYSTEM                           ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    print_info "Updating package lists..."
    pkg update -y
    
    print_info "Upgrading packages..."
    pkg upgrade -y
    
    print_status "System updated successfully!"
}

#===============================================================================
# Install System Dependencies
#===============================================================================

install_system_deps() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                 INSTALLING SYSTEM DEPENDENCIES              ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    # Core tools
    print_info "Installing core tools..."
    pkg install -y \
        build-essential \
        git \
        curl \
        wget \
        tar \
        unzip \
        zip \
        vim \
        nano \
        htop \
        termux-api \
        python \
        python-pip \
        libffi \
        libxml2 \
        libxslt \
        openssl \
        rust \
        cargo
    
    # Additional libraries for compilation
    print_info "Installing compilation dependencies..."
    pkg install -y \
        cmake \
        ninja \
        clang
    
    # Storage optimizer
    print_info "Cleaning up package cache..."
    pkg clean
    
    print_status "System dependencies installed!"
}

#===============================================================================
# Install Python Dependencies
#===============================================================================

install_python_deps() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                INSTALLING PYTHON DEPENDENCIES               ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Core dependencies
    print_info "Installing core Python packages..."
    pip install \
        requests \
        rich \
        typer \
        click \
        prompt_toolkit \
        pygments \
        transformers \
        torch \
        numpy \
        scipy
    
    # llama.cpp Python bindings (CPU optimized for mobile)
    print_info "Installing llama-cpp-python (this may take a while)..."
    pip install llama-cpp-python \
        --force-reinstall \
        --no-cache-dir \
        --verbose \
        CMAKE_ARGS="-DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_SERVER=OFF -DLLAMA_BUILD_TESTS=OFF" \
        LLAMA_CPP_PYTHON_LIB_DIR="auto"
    
    # Additional utilities
    print_info "Installing utilities..."
    pip install \
        tiktoken \
        sentencepiece \
        accelerate \
        peft \
        bitsandbytes
    
    print_status "Python dependencies installed!"
}

#===============================================================================
# Setup Zord Directory Structure
#===============================================================================

setup_directories() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                   SETTING UP DIRECTORIES                     ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    print_info "Creating Zord Coder directory structure..."
    
    mkdir -p "$MODEL_DIR"
    mkdir -p "$CACHE_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$ZORD_DIR/scripts"
    mkdir -p "$ZORD_DIR/src"
    mkdir -p "$ZORD_DIR/config"
    mkdir -p "$ZORD_DIR/data"
    
    # Create .env file
    cat > "$ZORD_DIR/.env" << 'EOF'
# Zord Coder v1 Environment Configuration

# Model Configuration
ZORD_MODEL_PATH="$HOME/zordcoder/models/zordcoder-v1-q4_k_m.gguf"
ZORD_CONTEXT_LENGTH=2048
ZORD_MAX_TOKENS=1024

# Generation Settings
ZORD_TEMPERATURE=0.1
ZORD_TOP_P=0.9
ZORD_TOP_K=40
ZORD_REPEAT_PENALTY=1.1

# Performance
ZORD_N_THREADS=4
ZORD_N_GPU_LAYERS=0
ZORD_N_BATCH=512

# Cache
ZORD_CACHE_DIR="$HOME/zordcoder/cache"

# Logging
ZORD_LOG_LEVEL=INFO
ZORD_LOG_FILE="$HOME/zordcoder/logs/zord.log"
EOF
    
    # Create .gitignore
    cat > "$ZORD_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Model files
*.gguf
*.bin
*.pt
*.pth
*.ckpt

# Cache
.cache/
*.log

# Environment
.env

# OS
.DS_Store
Thumbs.db
EOF
    
    print_status "Directory structure created!"
    print_info "Model directory: $MODEL_DIR"
    print_info "Cache directory: $CACHE_DIR"
    print_info "Log directory: $LOG_DIR"
}

#===============================================================================
# Download Model
#===============================================================================

download_model() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                      DOWNLOADING MODEL                       ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    MODEL_FILE="zordcoder-v1-q4_k_m.gguf"
    MODEL_PATH="$MODEL_DIR/$MODEL_FILE"
    
    if [ -f "$MODEL_PATH" ]; then
        print_status "Model already exists: $MODEL_PATH"
        return
    fi
    
    print_warning "No model file found!"
    print_info "You need to download a GGUF model to use Zord Coder."
    echo ""
    print_info "Recommended models (run on PC with more bandwidth):"
    echo "  1. DeepSeek-Coder-1.3B-Instruct-Q4_K_M.gguf"
    echo "     https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF"
    echo ""
    echo "  2. Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    echo "     https://huggingface.co/TheBloke/Qwen2-1.5B-Instruct-GGUF"
    echo ""
    echo "After downloading, place the GGUF file in: $MODEL_DIR"
    echo ""
    
    # Try to download a small test model or use wget
    print_info "Attempting to download a compatible model..."
    
    # HuggingFace CLI download (if available)
    if command -v huggingface-cli &> /dev/null; then
        print_info "Using huggingface-cli to download..."
        huggingface-cli download TheBloke/deepseek-coder-1.3b-instruct-GGUF \
            deepseek-coder-1.3b-instruct-q4_k_m.gguf \
            --local-dir "$MODEL_DIR" \
            --local-dir-use-symlinks False
    else
        print_warning "huggingface-cli not found."
        print_info "Please download the model manually and place it in: $MODEL_DIR"
        print_info "See: https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF"
    fi
}

#===============================================================================
# Install Zord Source Files
#===============================================================================

install_zord_source() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                   INSTALLING ZORD SOURCE FILES                ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    print_info "Installing Zord Coder Python package..."
    
    # Create setup.py
    cat > "$ZORD_DIR/setup.py" << 'EOF'
from setuptools import setup, find_packages

setup(
    name="zordcoder",
    version="1.0.0",
    description="Zord Coder - Ultimate Termux Coding Assistant",
    author="Zord Coder Team",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "llama-cpp-python>=0.2.0",
        "typer>=0.9.0",
        "pygments>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "zord=zordcoder.cli:main",
        ],
    },
    python_requires=">=3.9",
)
EOF
    
    # Create __init__.py
    touch "$ZORD_DIR/src/__init__.py"
    
    # Install in development mode
    cd "$ZORD_DIR"
    pip install -e .
    
    print_status "Zord Coder installed!"
}

#===============================================================================
# Configure Environment Variables
#===============================================================================

configure_environment() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                  CONFIGURING ENVIRONMENT                      ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    # Add to bashrc
    ZORD_BASHRC="
# Zord Coder v1 Environment
export ZORD_HOME=\"$ZORD_DIR\"
export ZORD_MODEL_PATH=\"$MODEL_DIR/zordcoder-v1-q4_k_m.gguf\"
export ZORD_CACHE_DIR=\"$CACHE_DIR\"
export ZORD_LOG_LEVEL=\"INFO\"

# Python optimization for mobile
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# llama.cpp optimization
export LLAMA_CPP_LIB=\"$HOME/.local/lib/python3.*/site-packages/llama_cpp/llama-cpp-python/lib/libllama.so\"
"
    
    # Check if already configured
    if grep -q "Zord Coder v1" ~/.bashrc 2>/dev/null; then
        print_status "Environment already configured in ~/.bashrc"
    else
        echo "$ZORD_BASHRC" >> ~/.bashrc
        print_status "Environment configured in ~/.bashrc"
    fi
    
    # Create convenient alias
    if ! grep -q "alias zord=" ~/.bashrc 2>/dev/null; then
        echo "alias zord='cd $ZORD_DIR && python3 -m zordcoder.cli'" >> ~/.bashrc
    fi
    
    print_info "Environment variables set:"
    print_info "  ZORD_HOME=$ZORD_DIR"
    print_info "  ZORD_MODEL_PATH=$MODEL_DIR/zordcoder-v1-q4_k_m.gguf"
}

#===============================================================================
# Performance Optimization
#===============================================================================

optimize_performance() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}               PERFORMANCE OPTIMIZATION                       ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    # Create optimized termux properties
    TERMUX_PROPS="$HOME/.termux/termux.properties"
    
    if [ ! -f "$TERMUX_PROPS" ]; then
        mkdir -p "$HOME/.termux"
        touch "$TERMUX_PROPS"
    fi
    
    # Enable extra keys
    if ! grep -q "extra-keys-style" "$TERMUX_PROPS" 2>/dev/null; then
        cat >> "$TERMUX_PROPS" << 'EOF'
extra-keys-style = arrows-all
allow-external-apps = true
EOF
    fi
    
    # Create performance tuning script
    cat > "$ZORD_DIR/scripts/tune_performance.sh" << 'EOF'
#!/bin/bash
# Zord Coder - Performance Tuning Script
# Run this to optimize your device for Zord Coder

echo "Optimizing Zord Coder performance..."

# Set Python to use all CPU cores efficiently
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Enable memory optimization
export PYTHONMALLOC=mem_debug

# Disable GPU (Termux typically doesn't have GPU support)
export LLAMA_CPP_NO_GPU=1

echo "Performance tuned for your device!"
EOF
    
    chmod +x "$ZORD_DIR/scripts/tune_performance.sh"
    
    print_status "Performance optimization configured!"
    print_info "Run 'bash scripts/tune_performance.sh' for optimal performance"
}

#===============================================================================
# Final Setup
#===============================================================================

final_setup() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                      FINAL SETUP                             ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    # Copy source files if not already there
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ -f "$SCRIPT_DIR/src/zord_core.py" ] && [ ! -f "$ZORD_DIR/src/zord_core.py" ]; then
        cp -r "$SCRIPT_DIR/src/"* "$ZORD_DIR/src/"
        print_status "Source files copied"
    fi
    
    if [ -f "$SCRIPT_DIR/scripts/zord_cli.py" ] && [ ! -f "$ZORD_DIR/src/cli.py" ]; then
        cp "$SCRIPT_DIR/scripts/zord_cli.py" "$ZORD_DIR/src/cli.py"
        print_status "CLI files copied"
    fi
    
    # Create main entry point
    cat > "$ZORD_DIR/zord.py" << 'EOF'
#!/usr/bin/env python3
"""
Zord Coder v1 - Main Entry Point
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli import main

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$ZORD_DIR/zord.py"
    
    print_status "Main entry point created: $ZORD_DIR/zord.py"
}

#===============================================================================
# Usage Instructions
#===============================================================================

print_usage() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                       USAGE GUIDE                             ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}\n"
    
    echo -e "${GREEN}Quick Start:${NC}"
    echo "  cd $ZORD_DIR"
    echo "  python3 zord.py"
    echo ""
    
    echo -e "${GREEN}Interactive Mode:${NC}"
    echo "  python3 -m zordcoder.cli"
    echo ""
    
    echo -e "${GREEN}Command Line:${NC}"
    echo "  python3 zord.py generate --prompt 'Write a Python hello world'"
    echo ""
    
    echo -e "${GREEN}First Time Setup:${NC}"
    echo "  1. Download a GGUF model file"
    echo "  2. Place it in: $MODEL_DIR"
    echo "  3. Rename it to: zordcoder-v1-q4_k_m.gguf"
    echo "  4. Run: python3 zord.py"
    echo ""
    
    echo -e "${YELLOW}Model Download Links:${NC}"
    echo "  DeepSeek-Coder-1.3B: https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF"
    echo "  Qwen2.5-1.5B:        https://huggingface.co/TheBloke/Qwen2-1.5B-Instruct-GGUF"
    echo ""
    
    echo -e "${GREEN}Help:${NC}"
    echo "  python3 zord.py --help"
    echo ""
}

#===============================================================================
# Main Execution
#===============================================================================

main() {
    print_banner
    
    echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}           ZORD CODER v1 - TERMUX SETUP SCRIPT              ${NC}"
    echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Run all setup steps
    check_environment
    update_system
    install_system_deps
    install_python_deps
    setup_directories
    download_model
    configure_environment
    optimize_performance
    final_setup
    
    echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                    SETUP COMPLETE!                           ${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    print_usage
    
    echo -e "${CYAN}Thank you for installing Zord Coder v1!${NC}"
    echo -e "${CYAN}Happy coding! 🚀${NC}"
    echo ""
}

# Run main
main "$@"
