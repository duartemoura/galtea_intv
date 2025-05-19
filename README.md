# Galtea Interview

A document-oriented chat application that uses OpenAI's GPT model to answer questions about uploaded documents. The system provides accurate, evidence-based information by grounding its answers in the provided documents and offering citations.

## Features

- Retrieval-augmented generation for grounded, trustworthy answers
- Citations with clickable sources
- Document upload and management via UI
- Conversation history and memory
- Hybrid retrieval (dense + sparse + re-ranking)
- Responsive and user-friendly interface

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/galtea_intv.git
cd galtea_intv
```

2. Create your virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```sh
touch .env
```

5. Add your environment variables to the `.env` file:
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (will use defaults if not set)
DOCUMENTS_DIR=documents
TEMP_DIR=temp
DB_DIR=db
MODEL_NAME=gpt-3.5-turbo
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
APP_TITLE=Galtea Interview
APP_HEADER=Duarte Moura
APP_VERSION=v1.0
```

## Usage

To launch the application:
```sh
streamlit run ui/streamlit_app.py
```

You can then:
- Upload documents (PDF format)
- Ask questions about the uploaded documents
- View answers with citations
- Manage your document collection

## Project Structure

```
galtea_intv/
├── src/
│   ├── __init__.py
│   ├── chatbot.py      # ChatBot class and logic
│   ├── config.py       # Configuration and environment variables
│   ├── core.py         # Core application logic
│   └── db.py          # Vector database implementation
├── ui/
│   ├── __init__.py
│   ├── sidebar.py     # Sidebar UI component
│   ├── tab1.py        # Chat interface
│   ├── tab2.py        # Document management
│   └── streamlit_app.py # Main application
├── documents/         # Document storage
├── temp/             # Temporary files
├── db/               # Vector database storage
├── .env              # Environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

## Core Components

### ChatBot
The ChatBot class handles:
- Message processing and context management
- Conversation history
- Integration with OpenAI's API
- Response generation with citations

### Vector Database
The vector database (Chroma) provides:
- Document storage and retrieval
- Semantic search capabilities
- Document chunking and embedding
- Context retrieval for responses

## Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `DOCUMENTS_DIR`: Directory for storing uploaded documents (default: 'documents')
- `TEMP_DIR`: Directory for temporary files (default: 'temp')
- `DB_DIR`: Directory for vector database (default: 'db')
- `MODEL_NAME`: OpenAI model to use (default: 'gpt-3.5-turbo')
- `EMBEDDING_MODEL`: Model for text embeddings (default: 'sentence-transformers/all-mpnet-base-v2')
- `APP_TITLE`: Application title (default: 'Galtea Interview')
- `APP_HEADER`: Application header (default: 'Duarte Moura')
- `APP_VERSION`: Application version (default: 'v1.0')

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
