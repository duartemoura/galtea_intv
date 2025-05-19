import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv(override=True)

# OpenAI API Key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Model configuration
CHAT_MODEL_NAME = "gpt-4.1-mini"  # Default model for chat interactions
RAG_DECISION_MODEL_NAME = "gpt-4o-mini"  # Model for deciding whether to use RAG
SUMMARY_MODEL_NAME = "gpt-4.1-nano"  # Model for document summarization

# Document storage
DOCUMENTS_DIR = "docs"
TEMP_DIR = "temp"

# Create necessary directories if they don't exist
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True) 