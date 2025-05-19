import streamlit as st
import time

def source_display_check(message):
    """
    Check if sources should be displayed based on their availability.
    
    Args:
        message (dict): The message containing content and sources
        
    Returns:
        bool: True if sources should be displayed, False otherwise
    """
    # Check if sources exist and are not empty
    return "sources" in message and message["sources"] and len(message["sources"]) > 0

def display_message(message):
    """Display a single chat message with its sources if any."""
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])
        # Only check for sources in assistant messages
        if message["role"] == "assistant":
            if source_display_check(message):
                with st.expander("View Sources"):
                    for idx, source in enumerate(message["sources"], 1):
                        st.markdown(
                            f'''<div style="font-size:16px; color:#555;">
<strong>Source {idx}:</strong><br/>
File: <code>{source['source']}</code><br/>
Preview: <em>{source['content']}</em><br/>
<hr/>
</div>''',
                            unsafe_allow_html=True,
                        )
            else:
                with st.expander("View Sources"):
                    st.markdown("No sources available for this message.")

def render_chat_tab():
    """Render the chat interface tab."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.markdown("""
            <h4>Hello, ask me a question!</h4>
        """, unsafe_allow_html=True)

    # Display existing chat history above the input
    for message in st.session_state.messages:
        display_message(message)

    # Place chat input below messages for follow-ups
    prompt = st.chat_input("Type your question here...")
    if prompt:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Process message using GalteaChat
        with st.spinner("Processing..."):
            try:
                response, sources = st.session_state.chat.process_message(
                    prompt,
                    history=st.session_state.messages[:-1]  # Exclude the current message
                )

                # Append assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })
            except Exception as e:
                st.error(f"Error processing message: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error: {str(e)}",
                    "sources": []
                })

        # Rerun to render updated messages above the input
        st.rerun()
    
    # Clear Chat button next to the chat
    if st.button("Clear Chat"):
        try:
            st.session_state.messages = []
            st.session_state.chat.reset()
            st.success("Chat cleared!")
        except Exception as e:
            st.error(f"Error clearing chat: {str(e)}")
        st.rerun()
