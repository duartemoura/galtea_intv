import streamlit as st
import pandas as pd
import time
import os
from src.config import TEMP_DIR

def render_documents_tab():
    """Render the document management interface tab."""
    st.header("📄 Document Management")
    
    # Get current documents
    documents = st.session_state.chat.list_documents()
    num_docs = len(documents)
    
    # Document list section first
    st.subheader("Current Document")
    if documents:
        st.info(f"📑 Currently loaded: **{documents[0]}**")
        
        # Initialize session state for deletion if not exists
        if 'doc_to_delete' not in st.session_state:
            st.session_state.doc_to_delete = None
        
        # Create a container for the delete confirmation
        delete_container = st.container()
        
        # Create a DataFrame with documents and add a delete button column
        df = pd.DataFrame([{"Name": doc} for doc in documents])
        df['Delete'] = False  # Add a column for delete buttons
        
        # Display the editable dataframe
        edited_df = st.data_editor(
            df,
            column_config={
                "Delete": st.column_config.CheckboxColumn(
                    "Delete",
                    help="Select to delete this document",
                    default=False,
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Check if any document is selected for deletion
        for i, row in edited_df.iterrows():
            if row['Delete']:
                st.session_state.doc_to_delete = row['Name']
                break
        
        # Show confirmation dialog if a document is selected for deletion
        if st.session_state.doc_to_delete:
            with delete_container:
                st.markdown("---")
                st.warning(f"⚠️ You are about to delete: **{st.session_state.doc_to_delete}**")
                st.markdown("This action cannot be undone.")
                
                col1, col2 = st.columns([1,2])
                with col1:
                    if st.button("✅ Confirm Delete", type="primary"):
                        try:
                            with st.spinner("Deleting document..."):
                                success = st.session_state.chat.delete_document(st.session_state.doc_to_delete)
                                if success:
                                    st.success(f"✅ Successfully deleted: {st.session_state.doc_to_delete}")
                                    st.session_state.doc_to_delete = None
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("❌ Error deleting document")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                with col2:
                    if st.button("❌ Cancel", type="secondary"):
                        st.session_state.doc_to_delete = None
                        st.rerun()
    else:
        st.info("No document is currently loaded. Upload a PDF to get started!")
    
    # Upload section
    st.markdown("---")
    st.subheader("📤 Upload New Document")
    
    if num_docs > 0:
        st.warning("⚠️ Please delete the current document before uploading a new one.")
        # Show disabled uploader
        st.file_uploader("Choose a PDF file (disabled - delete current document first)", type="pdf", disabled=True)
    else:
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            if st.button("Upload"):
                with st.spinner("Uploading document..."):
                    try:
                        # Save the uploaded file temporarily
                        temp_path = os.path.join(TEMP_DIR, uploaded_file.name)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        
                        # Upload using GalteaChat
                        success = st.session_state.chat.upload_document(temp_path)
                        
                        # Clean up
                        os.remove(temp_path)
                        
                        if success:
                            success_message = st.success("Document uploaded successfully!")
                            time.sleep(2)
                            success_message.empty()
                        else:
                            st.error("Error uploading document")
                    except Exception as e:
                        st.error(f"Error during upload: {str(e)}")
                        # Clean up temp file if it exists
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
