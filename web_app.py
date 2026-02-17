#!/usr/bin/env python3
"""
Zord Coder v1 - Web Application
Streamlit-based web interface for Zord Coder

Features:
- Beautiful x.ai-inspired theme (dark/light)
- Chat interface with streaming
- Code syntax highlighting
- Settings panel
- Performance metrics

Usage:
    streamlit run web_app.py
    # or
    python web_app.py
"""

import os
import sys
import time
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Any

import streamlit as st
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Zord Coder - AI Coding Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a Bug": None,
        "About": "Zord Coder v1 - Built by SaJad"
    }
)

# Try to import Zord Core
try:
    from src.zord_core import ZordCore, ZordConfig, GenerationConfig
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


#===============================================================================
# Custom CSS - x.ai Inspired Theme
#===============================================================================

def load_custom_css():
    """Load custom CSS for x.ai inspired styling"""
    
    # Get theme mode
    theme = st.session_state.get("theme", "dark")
    
    if theme == "dark":
        # Dark theme (x.ai inspired)
        bg_color = "#000000"
        surface_color = "#0A0A0A"
        text_color = "#FFFFFF"
        text_secondary = "#A0A0A0"
        accent_color = "#10B981"  # Green
        accent_hover = "#059669"
        border_color = "#1F1F1F"
        code_bg = "#111111"
    else:
        # Light theme
        bg_color = "#FFFFFF"
        surface_color = "#F9FAFB"
        text_color = "#111111"
        text_secondary = "#6B7280"
        accent_color = "#059669"  # Green
        accent_hover = "#047857"
        border_color = "#E5E7EB"
        code_bg = "#F3F4F6"
    
    custom_css = f"""
    <style>
    /* Main background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {surface_color};
        border-right: 1px solid {border_color};
    }}
    
    /* Chat messages */
    .chat-message {{
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }}
    
    .chat-message.user {{
        background-color: {surface_color};
        border-left: 3px solid {accent_color};
    }}
    
    .chat-message.assistant {{
        background-color: {surface_color};
        border-left: 3px solid {accent_color};
    }}
    
    /* Input field */
    .stTextInput input {{
        background-color: {surface_color};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 0.5rem;
    }}
    
    .stTextInput input:focus {{
        border-color: {accent_color};
        box-shadow: 0 0 0 2px {accent_color}40;
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {accent_color};
        color: white;
        border-radius: 0.5rem;
        border: none;
        font-weight: 500;
    }}
    
    .stButton button:hover {{
        background-color: {accent_hover};
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {text_color} !important;
    }}
    
    /* Links */
    a {{
        color: {accent_color};
    }}
    
    /* Code blocks */
    .stCodeBlock {{
        background-color: {code_bg};
        border-radius: 0.5rem;
    }}
    
    /* Dividers */
    hr {{
        border-color: {border_color};
    }}
    
    /* Toggle/Slider */
    .stSlider .stSlider-thumb {{
        background-color: {accent_color};
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {accent_color};
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {surface_color};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {border_color};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {accent_color};
    }}
    
    /* Markdown content */
    .stMarkdown p {{
        color: {text_color};
    }}
    
    /* Streamlit native elements styling */
    div[data-testid="stChatMessage"] {{
        background-color: {surface_color};
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    /* Status indicator */
    .status-indicator {{
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }}
    
    .status-indicator.ready {{
        background-color: #10B981;
    }}
    
    .status-indicator.loading {{
        background-color: #F59E0B;
    }}
    
    .status-indicator.error {{
        background-color: #EF4444;
    }}
    
    /* Custom title */
    .zord-title {{
        font-size: 2rem;
        font-weight: 700;
        color: {accent_color};
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    
    .zord-subtitle {{
        font-size: 1rem;
        color: {text_secondary};
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{
        visibility: hidden;
    }}
    
    footer {{
        visibility: hidden;
    }}
    
    .stDeployButton {{
        display: none;
    }}
    
    /* Loading animation */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    .loading {{
        animation: pulse 1.5s ease-in-out infinite;
    }}
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)


#===============================================================================
# Session State Management
#===============================================================================

def init_session_state():
    """Initialize session state variables"""
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "engine" not in st.session_state:
        st.session_state.engine = None
    
    if "config" not in st.session_state:
        st.session_state.config = None
    
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    
    if "model_loaded" not in st.session_state:
        st.session_state.model_loaded = False
    
    if "reasoning_mode" not in st.session_state:
        st.session_state.reasoning_mode = False
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.1
    
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 2048


#===============================================================================
# Model Management
#===============================================================================

@st.cache_resource
def load_zord_engine():
    """Load Zord Coder engine (cached)"""
    
    if not CORE_AVAILABLE:
        return None, None
    
    try:
        # Get model path
        model_path = os.getenv("ZORD_MODEL_PATH", "models/zordcoder-v1-q4_k_m.gguf")
        
        # Check if model exists
        if not os.path.exists(model_path):
            return None, None
        
        # Create config
        config = ZordConfig(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
        )
        
        # Create engine
        engine = ZordCore(config)
        
        # Load model
        if engine.load_model():
            return engine, config
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None


def check_and_download_model():
    """Check and download model if needed"""
    
    model_path = os.getenv("ZORD_MODEL_PATH", "models/zordcoder-v1-q4_k_m.gguf")
    
    if os.path.exists(model_path):
        return True
    
    # Try to download
    try:
        from scripts.download_model import check_and_download
        result = check_and_download()
        return result is not None
    except Exception as e:
        st.error(f"Error downloading model: {e}")
        return False


#===============================================================================
# UI Components
#===============================================================================

def render_header():
    """Render the header with logo and title"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="zord-title">🤖 Zord Coder</div>
        <div class="zord-subtitle">AI Coding Assistant by SaJad</div>
        """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings"""
    
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Theme toggle
        st.subheader("🎨 Appearance")
        theme = st.radio(
            "Theme",
            ["dark", "light"],
            index=0 if st.session_state.theme == "dark" else 1,
            horizontal=True
        )
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()
        
        st.divider()
        
        # Generation settings
        st.subheader("⚡ Generation")
        
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Higher values make output more random"
        )
        
        st.session_state.max_tokens = st.slider(
            "Max Tokens",
            min_value=256,
            max_value=4096,
            value=st.session_state.max_tokens,
            step=256,
            help="Maximum tokens to generate"
        )
        
        st.session_state.reasoning_mode = st.toggle(
            "🧠 Reasoning Mode",
            value=st.session_state.reasoning_mode,
            help="Enable chain-of-thought reasoning"
        )
        
        st.divider()
        
        # Model info
        st.subheader("📊 Model Info")
        
        if st.session_state.model_loaded:
            st.success("✅ Model Loaded")
            if st.button("🔄 Reload Model"):
                st.session_state.engine = None
                st.session_state.model_loaded = False
                st.rerun()
        else:
            st.warning("⚠️ Model Not Loaded")
            if st.button("📥 Load Model"):
                with st.spinner("Loading model..."):
                    engine, config = load_zord_engine()
                    if engine:
                        st.session_state.engine = engine
                        st.session_state.config = config
                        st.session_state.model_loaded = True
                        st.success("Model loaded successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to load model")
        
        st.divider()
        
        # Clear chat
        st.subheader("🗑️ Chat")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Stats
        if st.session_state.messages:
            st.divider()
            st.caption(f"Messages: {len(st.session_state.messages)}")


def render_chat():
    """Render the chat interface"""
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                # Assistant message - render with code highlighting
                render_assistant_message(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask Zord Coder anything..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            response = generate_response(prompt)
            render_assistant_message(response)
            
            # Add to messages
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })


def render_assistant_message(content: str):
    """Render assistant message with code highlighting"""
    
    # Check for code blocks
    if "```" in content:
        # Use Streamlit's markdown with code
        st.markdown(content)
    else:
        # Plain text
        st.markdown(content)


def generate_response(prompt: str) -> str:
    """Generate response from Zord Coder"""
    
    if not st.session_state.engine:
        return "⚠️ Model not loaded. Please load the model first."
    
    # Prepare prompt with reasoning mode
    if st.session_state.reasoning_mode:
        prompt = f"Let me think through this step by step:\n\n{prompt}"
    
    # Create generation config
    gen_config = GenerationConfig(
        temperature=st.session_state.temperature,
        max_tokens=st.session_state.max_tokens,
        repeat_penalty=1.1,
        stream=False,
    )
    
    try:
        # Generate response
        response, metrics = st.session_state.engine.generate_response(prompt, gen_config)
        
        # Show metrics (optional)
        with st.expander("📊 Generation Stats"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tokens", metrics.get("tokens_generated", 0))
            with col2:
                st.metric("Time", f"{metrics.get('generation_time', 0):.2f}s")
            with col3:
                st.metric("Speed", f"{metrics.get('tokens_per_second', 0):.1f} tok/s")
        
        return response
        
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"


def render_welcome():
    """Render welcome message when no messages"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>👋 Welcome to Zord Coder!</h2>
        <p style="color: #A0A0A0;">
            Your AI coding assistant is ready to help.<br>
            Start by typing a message below!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick suggestions
    st.subheader("💡 Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Write a Python function"):
            handle_quick_prompt("Write a Python function to calculate factorial")
    
    with col2:
        if st.button("🐛 Help debug code"):
            handle_quick_prompt("Help me debug this JavaScript code")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("❓ Explain a concept"):
            handle_quick_prompt("Explain what is recursion in programming")
    
    with col4:
        if st.button("🔧 Best practices"):
            handle_quick_prompt("What are the best practices for Python?")


def handle_quick_prompt(prompt: str):
    """Handle quick prompt button click"""
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Generate response
    with st.chat_message("assistant"):
        response = generate_response(prompt)
        render_assistant_message(response)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
    
    st.rerun()


#===============================================================================
# Main Application
#===============================================================================

def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Load custom CSS
    load_custom_css()
    
    # Try to load model silently
    if CORE_AVAILABLE and not st.session_state.model_loaded:
        engine, config = load_zord_engine()
        if engine:
            st.session_state.engine = engine
            st.session_state.config = config
            st.session_state.model_loaded = True
    
    # Render UI
    render_sidebar()
    
    # Main content area
    if st.session_state.messages:
        render_chat()
    else:
        render_welcome()


# Entry point
if __name__ == "__main__":
    main()
