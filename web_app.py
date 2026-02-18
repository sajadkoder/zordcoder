#!/usr/bin/env python3
"""
Zord Coder v1 - Web Application
Streamlit-based web interface for Zord Coder

Features:
- Beautiful x.ai-inspired theme (dark/light)
- Chat interface with streaming
- Code syntax highlighting
- Usage limits per user (no auth)
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
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from collections import defaultdict

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
# Usage Limits Configuration
#===============================================================================

class UsageLimiter:
    """Simple usage limiter based on session/IP"""
    
    def __init__(self):
        # Free tier limits
        self.MAX_MESSAGES_PER_DAY = 50
        self.MAX_TOKENS_PER_DAY = 50000
        self.MAX_REQUESTS_PER_MINUTE = 10
        
        # Initialize session state for usage tracking
        if "usage" not in st.session_state:
            st.session_state.usage = {
                "messages_today": 0,
                "tokens_today": 0,
                "last_reset": datetime.now().date(),
                "requests_this_minute": 0,
                "last_request_time": None
            }
        
        # Reset daily counters if new day
        self._check_daily_reset()
    
    def _check_daily_reset(self):
        """Reset counters if it's a new day"""
        today = datetime.now().date()
        if st.session_state.usage["last_reset"] != today:
            st.session_state.usage = {
                "messages_today": 0,
                "tokens_today": 0,
                "last_reset": today,
                "requests_this_minute": 0,
                "last_request_time": None
            }
    
    def can_send_message(self) -> tuple[bool, str]:
        """Check if user can send a message"""
        usage = st.session_state.usage
        
        # Check daily message limit
        if usage["messages_today"] >= self.MAX_MESSAGES_PER_DAY:
            return False, f"Daily message limit reached ({self.MAX_MESSAGES_PER_DAY} messages/day). Come back tomorrow!"
        
        # Check daily token limit
        if usage["tokens_today"] >= self.MAX_TOKENS_PER_DAY:
            return False, f"Daily token limit reached ({self.MAX_TOKENS_PER_DAY} tokens/day). Come back tomorrow!"
        
        # Check rate limit
        current_time = time.time()
        if usage["last_request_time"]:
            time_diff = current_time - usage["last_request_time"]
            
            if time_diff < 60:  # Within same minute
                if usage["requests_this_minute"] >= self.MAX_REQUESTS_PER_MINUTE:
                    return False, "Too many requests. Please wait a minute."
        
        return True, ""
    
    def record_usage(self, tokens: int):
        """Record usage after a request"""
        usage = st.session_state.usage
        current_time = time.time()
        
        # Update counters
        usage["messages_today"] += 1
        usage["tokens_today"] += tokens
        
        # Reset minute counter if needed
        if usage["last_request_time"]:
            time_diff = current_time - usage["last_request_time"]
            if time_diff >= 60:
                usage["requests_this_minute"] = 0
        
        usage["requests_this_minute"] += 1
        usage["last_request_time"] = current_time
    
    def get_usage_info(self) -> Dict:
        """Get current usage information"""
        usage = st.session_state.usage
        return {
            "messages_used": usage["messages_today"],
            "messages_limit": self.MAX_MESSAGES_PER_DAY,
            "tokens_used": usage["tokens_today"],
            "tokens_limit": self.MAX_TOKENS_PER_DAY,
            "messages_remaining": self.MAX_MESSAGES_PER_DAY - usage["messages_today"],
            "tokens_remaining": self.MAX_TOKENS_PER_DAY - usage["tokens_today"]
        }


# Create global usage limiter
usage_limiter = UsageLimiter()


#===============================================================================
# Custom CSS - x.ai Inspired Theme (Enhanced)
#===============================================================================

def load_custom_css():
    """Load custom CSS for x.ai inspired styling"""
    
    # Get theme mode
    theme = st.session_state.get("theme", "dark")
    
    if theme == "dark":
        # Dark theme (x.ai inspired)
        bg_color = "#000000"
        surface_color = "#0A0A0A"
        surface_elevated = "#141414"
        text_color = "#FFFFFF"
        text_secondary = "#9CA3AF"
        text_muted = "#6B7280"
        accent_color = "#10B981"  # Green
        accent_hover = "#059669"
        accent_subtle = "#064E3B"
        border_color = "#1F1F1F"
        code_bg = "#111111"
        success_color = "#10B981"
        warning_color = "#F59E0B"
        error_color = "#EF4444"
    else:
        # Light theme
        bg_color = "#FFFFFF"
        surface_color = "#F9FAFB"
        surface_elevated = "#FFFFFF"
        text_color = "#111827"
        text_secondary = "#6B7280"
        text_muted = "#9CA3AF"
        accent_color = "#059669"
        accent_hover = "#047857"
        accent_subtle = "#D1FAE5"
        border_color = "#E5E7EB"
        code_bg = "#F3F4F6"
        success_color = "#059669"
        warning_color = "#D97706"
        error_color = "#DC2626"
    
    custom_css = f"""
    <style>
    /* Main background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {surface_color};
        border-right: 1px solid {border_color};
    }}
    
    [data-testid="stSidebar"] > div {{
        padding-top: 1rem;
    }}
    
    /* Chat container */
    .chat-container {{
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }}
    
    /* Chat messages - Enhanced */
    [data-testid="stChatMessage"] {{
        background-color: {surface_color};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid {border_color};
    }}
    
    [data-testid="stChatMessageContent"] {{
        padding: 0;
    }}
    
    /* User message */
    [data-testid="stChatMessage"]:has(div[data-testid="chatAvatar-avatar-user"]) {{
        background-color: {accent_subtle};
        border-color: {accent_color};
    }}
    
    /* Assistant message */
    [data-testid="stChatMessage"]:has(div[data-testid="chatAvatar-avatar-assistant"]) {{
        background-color: {surface_elevated};
    }}
    
    /* Avatar */
    [data-testid="chatAvatar-avatar-user"] {{
        background-color: {accent_color} !important;
    }}
    
    [data-testid="chatAvatar-avatar-assistant"] {{
        background-color: {surface_elevated} !important;
        border: 2px solid {accent_color};
    }}
    
    /* Input field */
    [data-testid="stChatInput"] {{
        background-color: {surface_color};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 0.75rem 1rem;
    }}
    
    [data-testid="stChatInput"]:focus-within {{
        border-color: {accent_color};
        box-shadow: 0 0 0 3px {accent_subtle};
    }}
    
    [data-testid="stChatInput"] input {{
        color: {text_color};
    }}
    
    [data-testid="stChatInput"] textarea {{
        color: {text_color} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {accent_color};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }}
    
    .stButton > button:hover {{
        background-color: {accent_hover};
        transform: translateY(-1px);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    /* Secondary buttons */
    .stButton.secondary > button {{
        background-color: transparent;
        border: 1px solid {border_color};
        color: {text_color};
    }}
    
    .stButton.secondary > button:hover {{
        background-color: {surface_elevated};
        border-color: {accent_color};
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
        font-weight: 600 !important;
    }}
    
    /* Dividers */
    hr {{
        border-color: {border_color};
        margin: 1.5rem 0;
    }}
    
    /* Sliders */
    .stSlider [data-baseweb="slider"] {{
        background-color: {border_color};
    }}
    
    .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background-color: {accent_color};
        border-color: {accent_color};
    }}
    
    /* Toggles */
    [data-testid="stToggleSwitch"] {{
        background-color: {border_color};
    }}
    
    [data-testid="stToggleSwitch"][aria-checked="true"] {{
        background-color: {accent_color};
    }}
    
    /* Metrics */
    [data-testid="stMetric"] {{
        background-color: {surface_elevated};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 1rem;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {text_secondary};
    }}
    
    [data-testid="stMetricValue"] {{
        color: {accent_color};
    }}
    
    /* Progress bar */
    .stProgress > div > div > div {{
        background-color: {accent_color};
    }}
    
    /* Spinner */
    .stSpinner {{
        color: {accent_color};
    }}
    
    /* Code blocks - Enhanced */
    pre {{
        background-color: {code_bg} !important;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid {border_color};
        overflow-x: auto;
    }}
    
    code {{
        background-color: {code_bg};
        color: {accent_color};
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.9em;
    }}
    
    pre code {{
        background-color: transparent;
        padding: 0;
        color: inherit;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {surface_color};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {border_color};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {text_muted};
    }}
    
    /* Markdown content */
    .stMarkdown p {{
        color: {text_color};
        line-height: 1.6;
    }}
    
    .stMarkdown a {{
        color: {accent_color};
    }}
    
    .stMarkdown a:hover {{
        color: {accent_hover};
    }}
    
    /* Info/Warning/Error boxes */
    [data-testid="stAlert"] {{
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Custom title styling */
    .main-title {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, {accent_color}, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    
    .main-subtitle {{
        font-size: 1.1rem;
        color: {text_secondary};
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    /* Usage bar */
    .usage-bar {{
        background-color: {surface_elevated};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    .usage-label {{
        color: {text_secondary};
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }}
    
    .usage-progress {{
        height: 8px;
        background-color: {border_color};
        border-radius: 4px;
        overflow: hidden;
    }}
    
    .usage-progress-fill {{
        height: 100%;
        background-color: {accent_color};
        border-radius: 4px;
        transition: width 0.3s ease;
    }}
    
    /* Quick action buttons */
    .quick-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin: 1rem 0;
    }}
    
    .quick-action-btn {{
        background-color: {surface_elevated};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 0.5rem 1rem;
        color: {text_secondary};
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .quick-action-btn:hover {{
        border-color: {accent_color};
        color: {accent_color};
    }}
    
    /* Welcome card */
    .welcome-card {{
        background-color: {surface_elevated};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }}
    
    /* Status badge */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }}
    
    .status-badge.ready {{
        background-color: {accent_subtle};
        color: {accent_color};
    }}
    
    .status-badge.warning {{
        background-color: #FEF3C7;
        color: {warning_color};
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .animate-in {{
        animation: fadeIn 0.3s ease-out;
    }}
    
    /* Hide elements */
    .hidden {{
        display: none;
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
        return None, None


#===============================================================================
# UI Components
#===============================================================================

def render_header():
    """Render the header with logo and title"""
    
    st.markdown("""
    <div class="main-title">🤖 Zord Coder</div>
    <div class="main-subtitle">AI Coding Assistant by SaJad</div>
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
            horizontal=True,
            label_visibility="collapsed"
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
        
        # Usage info
        st.subheader("📊 Today's Usage")
        
        usage_info = usage_limiter.get_usage_info()
        
        # Messages bar
        st.caption("Messages")
        messages_percent = (usage_info["messages_used"] / usage_info["messages_limit"]) * 100
        st.progress(min(messages_percent, 100))
        st.caption(f"{usage_info['messages_used']} / {usage_info['messages_limit']} messages")
        
        # Tokens bar
        st.caption("Tokens")
        tokens_percent = (usage_info["tokens_used"] / usage_info["tokens_limit"]) * 100
        st.progress(min(tokens_percent, 100))
        st.caption(f"{usage_info['tokens_used']:,} / {usage_info['tokens_limit']:,} tokens")
        
        st.divider()
        
        # Model status
        st.subheader("🤖 Model Status")
        
        if st.session_state.model_loaded:
            st.success("✅ Model Loaded")
        else:
            st.warning("⚠️ Model Not Loaded")
            if st.button("📥 Load Model", use_container_width=True):
                with st.spinner("Loading model..."):
                    engine, config = load_zord_engine()
                    if engine:
                        st.session_state.engine = engine
                        st.session_state.config = config
                        st.session_state.model_loaded = True
                        st.success("Model loaded!")
                        st.rerun()
                    else:
                        st.error("Failed to load model")
        
        st.divider()
        
        # Clear chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_usage_limit_message():
    """Render usage limit exceeded message"""
    st.markdown("""
    <div class="welcome-card">
        <h2>🚫 Daily Limit Reached</h2>
        <p style="color: #9CA3AF; margin-top: 1rem;">
            You've reached your daily usage limit.<br>
            Come back tomorrow for more free generations!
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_welcome():
    """Render welcome message with quick actions"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="welcome-card animate-in">
            <h2>👋 Welcome to Zord Coder!</h2>
            <p style="color: #9CA3AF; margin-top: 0.5rem;">
                Your AI coding assistant is ready to help.<br>
                Start by typing a message below!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            if st.button("📝 Python", key="quick_python", use_container_width=True):
                handle_quick_prompt("Write a Python function to calculate factorial")
        
        with col_b:
            if st.button("🐛 Debug", key="quick_debug", use_container_width=True):
                handle_quick_prompt("Help me debug this JavaScript code")
        
        with col_c:
            if st.button("❓ Explain", key="quick_explain", use_container_width=True):
                handle_quick_prompt("Explain what is recursion in programming")
        
        with col_d:
            if st.button("🔧 Best Practices", key="quick_best", use_container_width=True):
                handle_quick_prompt("What are Python best practices?")
        
        st.markdown('</div>', unsafe_allow_html=True)


def handle_quick_prompt(prompt: str):
    """Handle quick prompt button click"""
    
    # Check usage limits
    can_send, error_msg = usage_limiter.can_send_message()
    if not can_send:
        st.error(error_msg)
        return
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Generate response
    response = generate_response(prompt)
    
    # Record usage
    usage_limiter.record_usage(len(response.split()))
    
    # Add to messages
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
    
    st.rerun()


def generate_response(prompt: str) -> str:
    """Generate response from Zord Coder"""
    
    if not st.session_state.engine:
        return "⚠️ Model not loaded. Please wait for the model to load or reload the page."
    
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
        return response
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


def render_chat():
    """Render the chat interface"""
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


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
    
    # Render sidebar
    render_sidebar()
    
    # Render header
    render_header()
    
    # Check usage limits for new messages
    can_send, error_msg = usage_limiter.can_send_message()
    
    # Chat input (disabled if limit reached)
    if prompt := st.chat_input(
        "Ask Zord Coder anything..." if can_send else error_msg,
        disabled=not can_send
    ):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Generate response
        response = generate_response(prompt)
        
        # Record usage
        usage_limiter.record_usage(len(response.split()))
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        
        st.rerun()
    
    # Show messages or welcome
    if st.session_state.messages:
        render_chat()
    else:
        render_welcome()


# Entry point
if __name__ == "__main__":
    main()
