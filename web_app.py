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
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Zord Coder - AI Coding Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Try to import Zord Core
try:
    from src.zord_core import ZordCore, ZordConfig, GenerationConfig
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    print("Warning: zord_core not found")


#===============================================================================
# Usage Limits
#===============================================================================

class UsageLimiter:
    def __init__(self):
        self.MAX_MESSAGES_PER_DAY = 50
        self.MAX_TOKENS_PER_DAY = 50000
        self.MAX_REQUESTS_PER_MINUTE = 10
        
        if "usage" not in st.session_state:
            st.session_state.usage = {
                "messages_today": 0,
                "tokens_today": 0,
                "last_reset": datetime.now().date(),
                "requests_this_minute": 0,
                "last_request_time": None
            }
        
        self._check_daily_reset()
    
    def _check_daily_reset(self):
        today = datetime.now().date()
        if st.session_state.usage["last_reset"] != today:
            st.session_state.usage = {
                "messages_today": 0,
                "tokens_today": 0,
                "last_reset": today,
                "requests_this_minute": 0,
                "last_request_time": None
            }
    
    def can_send_message(self):
        usage = st.session_state.usage
        
        if usage["messages_today"] >= self.MAX_MESSAGES_PER_DAY:
            return False, f"Daily limit reached ({self.MAX_MESSAGES_PER_DAY} messages). Come back tomorrow!"
        
        if usage["tokens_today"] >= self.MAX_TOKENS_PER_DAY:
            return False, f"Daily limit reached ({self.MAX_TOKENS_PER_DAY} tokens). Come back tomorrow!"
        
        current_time = time.time()
        if usage["last_request_time"]:
            time_diff = current_time - usage["last_request_time"]
            if time_diff < 60:
                if usage["requests_this_minute"] >= self.MAX_REQUESTS_PER_MINUTE:
                    return False, "Too many requests. Please wait a minute."
        
        return True, ""
    
    def record_usage(self, tokens: int):
        usage = st.session_state.usage
        current_time = time.time()
        
        usage["messages_today"] += 1
        usage["tokens_today"] += tokens
        
        if usage["last_request_time"]:
            time_diff = current_time - usage["last_request_time"]
            if time_diff >= 60:
                usage["requests_this_minute"] = 0
        
        usage["requests_this_minute"] += 1
        usage["last_request_time"] = current_time
    
    def get_usage_info(self):
        usage = st.session_state.usage
        return {
            "messages_used": usage["messages_today"],
            "messages_limit": self.MAX_MESSAGES_PER_DAY,
            "tokens_used": usage["tokens_today"],
            "tokens_limit": self.MAX_TOKENS_PER_DAY,
        }


usage_limiter = UsageLimiter()


#===============================================================================
# Custom CSS - Clean & Polished
#===============================================================================

def load_css():
    theme = st.session_state.get("theme", "dark")
    
    if theme == "dark":
        bg = "#000000"
        surface = "#0A0A0A"
        surface_hover = "#171717"
        text = "#FFFFFF"
        text_secondary = "#A3A3A3"
        accent = "#10B981"
        accent_hover = "#059669"
        accent_light = "#34D399"
        border = "#262626"
    else:
        bg = "#FAFAFA"
        surface = "#FFFFFF"
        surface_hover = "#F5F5F5"
        text = "#171717"
        text_secondary = "#737373"
        accent = "#059669"
        accent_hover = "#047857"
        accent_light = "#10B981"
        border = "#E5E5E5"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif !important;
    }}
    
    .stApp {{
        background: {bg};
        color: {text};
    }}
    
    /* Hide elements */
    #MainMenu, footer, .stDeployButton {{
        display: none !important;
    }}
    
    /* Main container */
    .main-content {{
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }}
    
    /* Title */
    .title-wrapper {{
        text-align: center;
        padding: 2rem 0 1rem;
    }}
    
    .main-title {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, {accent} 0%, {accent_light} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }}
    
    .main-subtitle {{
        color: {text_secondary};
        font-size: 1rem;
        margin-top: 0.5rem;
    }}
    
    /* Chat messages */
    [data-testid="stChatMessage"] {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
    }}
    
    [data-testid="stChatMessage"]:has([data-testid="chatAvatar-avatar-user"]) {{
        background: {surface_hover};
        border-color: {accent};
    }}
    
    /* Avatars */
    [data-testid="chatAvatar-avatar-user"] {{
        background: {accent} !important;
    }}
    
    [data-testid="chatAvatar-avatar-assistant"] {{
        background: {surface} !important;
        border: 2px solid {accent} !important;
    }}
    
    /* Chat input */
    [data-testid="stChatInput"] {{
        background: {surface};
        border: 2px solid {border};
        border-radius: 16px;
        padding: 0.75rem 1rem;
    }}
    
    [data-testid="stChatInput"]:focus-within {{
        border-color: {accent};
        box-shadow: 0 0 0 3px {accent}20;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: {accent};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s;
    }}
    
    .stButton > button:hover {{
        background: {accent_hover};
        transform: translateY(-1px);
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {surface};
        border-right: 1px solid {border};
    }}
    
    /* Sidebar sections */
    .sidebar-section {{
        padding: 1rem 0;
        border-bottom: 1px solid {border};
    }}
    
    .sidebar-title {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {text_secondary};
        margin-bottom: 0.75rem;
    }}
    
    /* Progress bars */
    .stProgress > div > div > div {{
        background: {accent};
    }}
    
    /* Metrics */
    [data-testid="stMetric"] {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 1rem;
    }}
    
    /* Welcome card */
    .welcome-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .welcome-card h2 {{
        color: {text};
        margin-bottom: 0.5rem;
    }}
    
    .welcome-card p {{
        color: {text_secondary};
    }}
    
    /* Quick actions */
    .quick-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 1.5rem;
    }}
    
    .quick-btn {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 999px;
        padding: 0.5rem 1rem;
        color: {text_secondary};
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .quick-btn:hover {{
        border-color: {accent};
        color: {accent};
    }}
    
    /* Divider */
    hr {{
        border-color: {border};
        margin: 1.5rem 0;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {border};
        border-radius: 3px;
    }}
    
    /* Streamlit overrides */
    .stTextInput > div > div {{
        background: {surface};
    }}
    
    .stRadio > div {{
        gap: 0.5rem;
    }}
    
    .stRadio > div > label {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .stRadio > div > label:hover {{
        border-color: {accent};
    }}
    
    .stRadio > div > label:has(input:checked) {{
        background: {accent};
        border-color: {accent};
        color: white;
    }}
    
    .stToggle {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 1rem;
    }}
    
    /* Model status */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 500;
    }}
    
    .status-ready {{
        background: {accent}20;
        color: {accent};
    }}
    
    .status-error {{
        background: #EF444420;
        color: #EF4444;
    }}
    
    /* Usage text */
    .usage-text {{
        font-size: 0.875rem;
        color: {text_secondary};
        text-align: center;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


#===============================================================================
# Session State
#===============================================================================

def init_state():
    defaults = {
        "messages": [],
        "engine": None,
        "config": None,
        "theme": "dark",
        "model_loaded": False,
        "model_loading": False,
        "reasoning_mode": False,
        "temperature": 0.1,
        "max_tokens": 2048,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


#===============================================================================
# Model Loading
#===============================================================================

@st.cache_resource
def get_engine():
    """Get or create the engine"""
    return load_engine()


def load_engine():
    """Load the model engine"""
    if not CORE_AVAILABLE:
        return None
    
    try:
        # Try multiple possible model paths
        possible_paths = [
            "models/zordcoder-v1-q4_k_m.gguf",
            os.path.join(os.path.dirname(__file__), "models", "zordcoder-v1-q4_k_m.gguf"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "zordcoder-v1-q4_k_m.gguf"),
            os.getenv("ZORD_MODEL_PATH", ""),
        ]
        
        # Filter empty paths
        possible_paths = [p for p in possible_paths if p]
        
        model_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                model_path = path
                break
        
        if not model_path:
            return None
        
        config = ZordConfig(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False,
        )
        
        engine = ZordCore(config)
        
        if engine.load_model():
            return engine
        
        return None
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


#===============================================================================
# UI Components
#===============================================================================

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
        
        # Theme
        theme = st.radio("Theme", ["dark", "light"], 
                        index=0 if st.session_state.theme == "dark" else 1,
                        horizontal=True, label_visibility="collapsed")
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()
        
        st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">⚡ Generation</div>', unsafe_allow_html=True)
        
        st.session_state.temperature = st.slider("Temperature", 0.0, 2.0, st.session_state.temperature, 0.1)
        st.session_state.max_tokens = st.slider("Max Tokens", 256, 4096, st.session_state.max_tokens, 256)
        st.session_state.reasoning_mode = st.toggle("🧠 Reasoning Mode", st.session_state.reasoning_mode)
        
        st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
        
        # Usage
        st.markdown('<div class="sidebar-title">📊 Today\'s Usage</div>', unsafe_allow_html=True)
        
        usage = usage_limiter.get_usage_info()
        
        st.caption("Messages")
        st.progress(usage["messages_used"] / usage["messages_limit"])
        st.caption(f"{usage['messages_used']} / {usage['messages_limit']}")
        
        st.caption("Tokens")
        st.progress(usage["tokens_used"] / usage["tokens_limit"])
        st.caption(f"{usage['tokens_used']:,} / {usage['tokens_limit']:,}")
        
        st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
        
        # Model status
        st.markdown('<div class="sidebar-title">🤖 Model</div>', unsafe_allow_html=True)
        
        if st.session_state.model_loaded:
            st.markdown('<span class="status-badge status-ready">✓ Loaded</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-error">○ Not Loaded</span>', unsafe_allow_html=True)
            
            if st.button("📥 Load Model", use_container_width=True):
                with st.spinner("Loading model..."):
                    st.session_state.model_loading = True
                    engine = get_engine()
                    if engine:
                        st.session_state.engine = engine
                        st.session_state.model_loaded = True
                        st.session_state.model_loading = False
                        st.rerun()
                    else:
                        st.session_state.model_loading = False
                        st.error("Failed to load model. Make sure model file exists in models/ folder.")
        
        st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_header():
    st.markdown(f"""
    <div class="title-wrapper">
        <h1 class="main-title">🤖 Zord Coder</h1>
        <p class="main-subtitle">AI Coding Assistant by SaJad</p>
    </div>
    """, unsafe_allow_html=True)


def render_welcome():
    st.markdown(f"""
    <div class="welcome-card">
        <h2>👋 Welcome!</h2>
        <p>Your AI coding assistant is ready. Start chatting below!</p>
        
        <div class="quick-actions">
            <a href="#" class="quick-btn" onclick="document.querySelector('[data-testid=stChatInput]').focus()">💬 Start Chatting</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def handle_quick_action(prompt):
    can_send, error = usage_limiter.can_send_message()
    if not can_send:
        st.error(error)
        return
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if st.session_state.engine and st.session_state.model_loaded:
        full_prompt = f"Let me think through this step by step:\n\n{prompt}" if st.session_state.reasoning_mode else prompt
        
        config = GenerationConfig(
            temperature=st.session_state.temperature,
            max_tokens=st.session_state.max_tokens,
            repeat_penalty=1.1,
            stream=False,
        )
        
        try:
            response, metrics = st.session_state.engine.generate_response(full_prompt, config)
            usage_limiter.record_usage(metrics.get("tokens_generated", 0))
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ Model not loaded. Please load the model first."})
    
    st.rerun()


#===============================================================================
# Main App
#===============================================================================

def main():
    init_state()
    load_css()
    
    # Try to load model
    if CORE_AVAILABLE and not st.session_state.model_loaded and not st.session_state.model_loading:
        with st.spinner("Loading model..."):
            engine = get_engine()
            if engine:
                st.session_state.engine = engine
                st.session_state.model_loaded = True
    
    render_sidebar()
    render_header()
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Python", use_container_width=True):
            handle_quick_action("Write a Python function to calculate factorial")
    with col2:
        if st.button("🐛 Debug", use_container_width=True):
            handle_quick_action("Help me debug this code")
    with col3:
        if st.button("❓ Explain", use_container_width=True):
            handle_quick_action("Explain recursion")
    with col4:
        if st.button("🔧 Best Practices", use_container_width=True):
            handle_quick_action("Python best practices")
    
    st.markdown("---")
    
    # Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Input
    can_send, error_msg = usage_limiter.can_send_message()
    
    if prompt := st.chat_input(
        "Ask Zord Coder anything..." if can_send else error_msg,
        disabled=not can_send
    ):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        if st.session_state.engine and st.session_state.model_loaded:
            full_prompt = f"Let me think through this step by step:\n\n{prompt}" if st.session_state.reasoning_mode else prompt
            
            config = GenerationConfig(
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
                repeat_penalty=1.1,
                stream=False,
            )
            
            try:
                response, metrics = st.session_state.engine.generate_response(full_prompt, config)
                usage_limiter.record_usage(metrics.get("tokens_generated", 0))
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "⚠️ Model not loaded. Please load the model from the sidebar."})
        
        st.rerun()


if __name__ == "__main__":
    main()
