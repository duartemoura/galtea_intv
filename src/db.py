# Import required libraries
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Tuple, Optional, Any
import os
import json
from .utils import summarize_document

# Class to handle vector database logic
class VectorDB:
    def __init__(self, persist_directory: str = "db"):
        """
        Initialize the vector store with:
        - a persistence directory to save vectors
        - a sentence-transformer model for embedding
        - a Chroma store to persist vectorized documents
        - a text splitter to chunk text
        """
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.summaries_file = os.path.join(persist_directory, "document_summaries.json")
        
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Load existing summaries if available
        self.document_summaries = self._load_summaries()
        
        # Create or load the vector store from the given directory
        self.vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=self.embeddings, 
            persist_directory=self.persist_directory
        )
        # Split long text into overlapping chunks
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        
        # If we have documents but no summaries, regenerate them
        if len(self.document_summaries) == 0:
            self._regenerate_summaries()
    
    def _load_summaries(self) -> Dict[str, str]:
        """Load document summaries from disk."""
        if os.path.exists(self.summaries_file):
            try:
                with open(self.summaries_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading summaries: {str(e)}")
        return {}
    
    def _save_summaries(self) -> None:
        """Save document summaries to disk."""
        try:
            with open(self.summaries_file, 'w') as f:
                json.dump(self.document_summaries, f)
        except Exception as e:
            print(f"Error saving summaries: {str(e)}")
    
    def _regenerate_summaries(self) -> None:
        """Regenerate summaries for all documents in the vector store."""
        try:
            results = self.vector_store.get()
            unique_sources = set()
            
            # Get unique document sources
            for metadata in results['metadatas']:
                if 'source' in metadata:
                    unique_sources.add(metadata['source'])
            
            # Generate summaries for each document
            for source in unique_sources:
                filename = os.path.basename(source)
                if filename not in self.document_summaries:
                    # Get all chunks for this document
                    doc_chunks = []
                    for i, metadata in enumerate(results['metadatas']):
                        if metadata.get('source') == source:
                            doc_chunks.append(results['documents'][i])
                    
                    # Generate summary
                    full_text = " ".join(doc_chunks)
                    summary = summarize_document(full_text)
                    self.document_summaries[filename] = summary
            
            # Save the regenerated summaries
            self._save_summaries()
            
        except Exception as e:
            print(f"Error regenerating summaries: {str(e)}")
    
    def upload_document(self, path_to_single_document: str) -> bool:
        """
        Load a single PDF document, split it into chunks, and add them to the vector store.
        Adds 'chunk_idx' metadata to each chunk for tracking and reordering.
        
        Args:
            path_to_single_document (str): Path to the PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(path_to_single_document):
                raise FileNotFoundError(f"Document not found: {path_to_single_document}")
                
            loader = PyPDFLoader(path_to_single_document, mode="single")
            documents = loader.load()
            
            # Generate a consolidated summary of the entire document
            full_text = " ".join([doc.page_content for doc in documents])
            document_summary = summarize_document(full_text)
            
            # Store the summary with the document filename as key
            filename = os.path.basename(path_to_single_document)
            self.document_summaries[filename] = document_summary
            self._save_summaries()  # Save summaries after updating
            
            # Split the document into chunks
            docs = self.text_splitter.split_documents(documents)

            for idx, doc in enumerate(docs):
                # Add metadata including the document summary
                doc.metadata["chunk_idx"] = idx
                doc.metadata["document_summary"] = document_summary
                
            # Store docs into Chroma - persistence is automatic now
            if len(docs) > 0:
                self.vector_store.add_documents(docs)
                return True
            return False
            
        except Exception as e:
            print(f"Error uploading document {path_to_single_document}: {str(e)}")
            return False
        
    def upload_documents(self, documents_paths: List[str]) -> bool:
        """
        Upload multiple PDF documents from a list of paths.
        
        Args:
            documents_paths (List[str]): List of paths to PDF files
            
        Returns:
            bool: True if all documents were uploaded successfully, False otherwise
        """
        try:
            success = True
            for path in documents_paths:
                if not self.upload_document(path):
                    success = False
            return success
        except Exception as e:
            print(f"Error uploading documents: {str(e)}")
            return False
            
    def retrieve_context(self, query: str, k: int = 3, chunk_window_size: int = 2) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Retrieve top-k most relevant chunks for the query, and expand them with nearby chunks.
        Also return a short source preview for reference.
        
        Args:
            query (str): The search query
            k (int): Number of top chunks to retrieve
            chunk_window_size (int): Number of nearby chunks to include
            
        Returns:
            Tuple[str, List[Dict[str, Any]]]: (context, sources)
        """
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            joined_chunks = []
            for doc in docs:
                joined_chunks.append(self._search_nearby_chunks(doc, chunk_window_size))
            context = "\n\n---\n\n".join(joined_chunks)
            
            # Extract source information from documents
            sources = []
            for doc in docs:
                # Extract just the filename from the full path
                full_source = doc.metadata.get("source", "Unknown")
                source_filename = os.path.basename(full_source)
                
                source_info = {
                    "source": source_filename,
                    "content": doc.page_content[:500] + "...",  # Preview of content
                    "metadata": doc.metadata
                }
                sources.append(source_info)
                
            return context, sources
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return "", []

    def _search_nearby_chunks(self, doc: Any, window: int) -> str:
        """
        Given a document chunk, find nearby chunks in the same PDF file (based on chunk_idx).
        This helps preserve context that might have been split.
        
        Args:
            doc: Document chunk
            window (int): Number of chunks to include before and after
            
        Returns:
            str: Joined text of nearby chunks
        """
        try:
            if hasattr(doc, "metadata"):
                source_doc = doc.metadata["source"]
            else:
                source_doc = doc["metadata"]["source"]
                
            # Get every chunk of the same pdf document.
            all_chunks = self.vector_store.get(where={"source": source_doc})

            unique_chunks = []
            unique_metadatas = []
            seen_keys = set()

            # For removing duplicates.
            for i, content in enumerate(all_chunks["documents"]):
                metadata = all_chunks["metadatas"][i]
                key = (metadata.get("source"), metadata.get("chunk_idx"))
                if key not in seen_keys:
                    seen_keys.add(key)
                    unique_chunks.append(content)
                    unique_metadatas.append(metadata)
            all_chunks["documents"] = unique_chunks
            all_chunks["metadatas"] = unique_metadatas
            
            # Create a list of tuples (chunk_idx, content) for sorting
            chunk_data = []
            for i, content in enumerate(all_chunks["documents"]):
                metadata = all_chunks["metadatas"][i]
                # Use chunk_idx if available, otherwise use position in list
                chunk_idx = float(metadata.get("chunk_idx", i))
                chunk_data.append((chunk_idx, content))

            # Sort chunks by chunk_idx
            chunk_data.sort(key=lambda x: x[0])

            # Get the current chunk's index
            if hasattr(doc, "metadata"):
                current_chunk_idx = float(doc.metadata.get("chunk_idx", 0))
            else:
                current_chunk_idx = float(doc["metadata"].get("chunk_idx", 0))
            
            nearby_chunks = []
            target_indices = set(range(int(current_chunk_idx - window), int(current_chunk_idx + window + 1)))
            for idx, content in chunk_data:
                if idx in target_indices:
                    nearby_chunks.append(content)

            cleaned_chunks = [nearby_chunks[0]]  # Keep the first chunk as-is

            for chunk in nearby_chunks[1:]:
                cleaned_chunks.append(chunk[self.text_splitter._chunk_overlap:])  # Remove the overlap

            return "".join(cleaned_chunks)
        except Exception as e:
            print(f"Error searching nearby chunks: {str(e)}")
            return ""

    def list_documents(self) -> List[str]:
        """
        List all unique source documents currently stored in the vector database.
        
        Returns:
            List[str]: List of document filenames
        """
        try:
            # Get all documents and their metadata
            results = self.vector_store.get()
            # Extract unique source documents
            documents = set()
            
            for metadata in results['metadatas']:
                if 'source' in metadata:
                    # Get just the filename from the full path
                    filename = os.path.basename(metadata['source'])
                    documents.add(filename)
                    
            return list(documents)
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []

    def get_all_summaries(self) -> str:
        """
        Get all document summaries concatenated together.
        
        Returns:
            str: Concatenated summaries of all documents
        """
        return "\n\n".join(self.document_summaries.values())

    def delete_document(self, filename: str) -> bool:
        """
        Delete a document from the vector store and its summary.
        
        Args:
            filename (str): Name of the document to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not filename or not filename.strip():
                raise ValueError("Filename cannot be empty")
                
            # Get all documents and their metadata
            results = self.vector_store.get()
            
            # Find all chunk IDs that belong to this document
            ids_to_delete = []
            for i, metadata in enumerate(results['metadatas']):
                if 'source' in metadata:
                    source_filename = os.path.basename(metadata['source'])
                    if source_filename == filename:
                        ids_to_delete.append(results['ids'][i])
            
            if not ids_to_delete:
                print(f"No document found with filename: {filename}")
                return False
            
            # Delete the chunks
            self.vector_store.delete(ids=ids_to_delete)
            
            # Remove the summary from our dictionary and save
            if filename in self.document_summaries:
                del self.document_summaries[filename]
                self._save_summaries()  # Save summaries after updating
                
            return True
            
        except Exception as e:
            print(f"Error deleting document {filename}: {str(e)}")
            return False