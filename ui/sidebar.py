import streamlit as st

def render_sidebar():
    """Render the sidebar content."""
    with st.sidebar:
        st.markdown("## Welcome")
        st.markdown("To use tis chatbot, you can directly chat with the model, or upload your documents and ask questions about them.")
        st.markdown("You can also go to the document tab to manage your documents.")
        st.markdown("---")
