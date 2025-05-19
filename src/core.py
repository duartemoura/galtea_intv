import os
import glob
from typing import List, Tuple, Optional, Dict
from .chatbot import ChatBot, Memory
from .db import VectorDB
from .utils import should_use_rag

class GalteaChat:
    def __init__(self, documents_dir: str = "data"):
        """
        Initialize the GalteaChat system.
        
        Args:
            documents_dir (str): Directory where PDF documents are stored
        """
        self.documents_dir = documents_dir
        self.chatbot = ChatBot()
        self.vector_db = VectorDB()
        
        # Load initial documents if collection is empty
        try:
            collection_size = len(self.vector_db.vector_store.get()["ids"])
            if collection_size == 0:
                documents = glob.glob(os.path.join(documents_dir, "*.pdf"))
                print(f"Loading initial documents: {documents}")
                for doc in documents:
                    self.vector_db.upload_document(doc)
                print("Initial documents loaded successfully")
            else:
                print(f"Using existing collection with {collection_size} documents")
        except Exception as e:
            print(f"Error initializing document collection: {str(e)}")
            raise

    def upload_document(self, file_path: str) -> bool:
        """
        Upload and process a new document.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not file_path.endswith(".pdf"):
                raise ValueError("Only PDF files are supported")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            self.vector_db.upload_document(file_path)
            return True
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            return False

    def process_message(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> Tuple[str, List[Dict[str, str]]]:
        """
        Process a user message and return the response.
        
        Args:
            message (str): The user's message
            history (List[Dict[str, str]], optional): Chat history in the format [{"role": "user/assistant", "content": "message"}]
            
        Returns:
            Tuple[str, List[Dict[str, str]]]: (response, sources)
        """
        try:
            if not message or not message.strip():
                raise ValueError("Message cannot be empty")

            # Get all document summaries
            summaries = self.vector_db.get_all_summaries()
            
            # Check if the message should use RAG
            if should_use_rag(message, summaries):
                # If RAG worthy, retrieve context and get response with sources
                self.chatbot.retrieve_context_from_db(message, self.vector_db)
                answer, sources = self.chatbot.infer(message, history=history)
                return answer, sources
            else:
                # If not RAG worthy, just get response without sources
                answer, _ = self.chatbot.infer(message, history=history)
                return answer, []
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(error_msg)
            return error_msg, []

    def list_documents(self) -> List[str]:
        """
        List all documents in the vector store.
        
        Returns:
            List[str]: List of document filenames
        """
        try:
            return self.vector_db.list_documents()
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []

    def delete_document(self, filename: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            filename (str): Name of the document to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not filename or not filename.strip():
                raise ValueError("Filename cannot be empty")
            return self.vector_db.delete_document(filename)
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False

    def reset(self) -> None:
        """
        Reset the chatbot's context and memory.
        """
        try:
            self.chatbot.remove_context()
            self.chatbot.memory.reset_memory()
        except Exception as e:
            print(f"Error resetting chatbot: {str(e)}")
            raise
