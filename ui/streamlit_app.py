import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core import GalteaChat
from src.config import DOCUMENTS_DIR, TEMP_DIR

# Import UI modules
from ui.sidebar import render_sidebar
from ui.tab1 import render_chat_tab
from ui.tab2 import render_documents_tab

# ---- Page Config ----
st.set_page_config(
    page_title="Galtea Interview",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- Custom CSS ----
st.markdown("""
    <style>
    .stApp { max-width: 1200px; margin: 0 auto; font-family: 'Segoe UI', Arial, sans-serif; }
    .main-header { text-align: center; color: #ff69b4; padding: 2rem 0; font-size: 2.5rem;}
    .sidebar-title { color: #ff69b4; font-weight: bold; font-size: 1.2rem;}
    .doc-list { background: #fff0f6; border-radius: 8px; padding: 1rem; }
    .upload-section { background: #f5f5f5; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;}
    .chat-container { background: #f5f5f5; border-radius: 10px; padding: 20px; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# Ensure required directories exist
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Initialize GalteaChat with configured documents directory
if "chat" not in st.session_state:
    try:
        st.session_state.chat = GalteaChat(documents_dir=DOCUMENTS_DIR)
    except Exception as e:
        st.error(f"Error initializing chat system: {str(e)}")
        st.stop()

# ---- Main Header ----
st.markdown("<h1 class='main-header'> Galtea Interview </h1>", unsafe_allow_html=True)
st.markdown("<h2 class='main-header'> Duarte Moura </h2>", unsafe_allow_html=True)

# ---- Render Sidebar ----
render_sidebar()

# ---- Tabs ----
tab1, tab2 = st.tabs(["🤖 Chat", "📄 Documents"])

# ---- Render Tabs ----
with tab1:
    render_chat_tab()

with tab2:
    render_documents_tab()
        
        




