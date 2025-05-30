# Galtea Interview - Simple RAG application

## Duarte Moura 

## Features

- Retrieval-augmented generation for grounded, trustworthy answers
- Citations with clickable sources
- Document upload and management via UI
- Conversation history and memory
- Responsive and user-friendly interface
- Docker support for easy deployment

## Installation

### Option 1: Local Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/galtea_intv.git
cd galtea_intv
```

2. Create your virtual environment:
```sh
python -m venv venv
source venv/bin/activate  
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
```

### Option 2: Docker Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/galtea_intv.git
cd galtea_intv
```

2. Create a `.env` file as described above

3. Build and run with Docker Compose:
```sh
docker-compose up --build
```

## Usage

To launch the application:

### Local:
```sh
streamlit run ui/streamlit_app.py
```

### Docker:
The application will be available at http://localhost:8501 after running `docker-compose up`

You can then:
- Upload documents (PDF format)
- Should only have 1 document in the db at a time
- Ask questions about the uploaded documents
- View answers with citations
- Manage your document collection

## Project Structure

```
galtea_intv/
├── src/
│   ├── __init__.py
│   ├── chatbot.py        # ChatBot class and logic
│   ├── config.py         # Configuration and environment variables
│   ├── core.py           # Core application logic
│   ├── db.py             # Vector database implementation
│   └── utils.py          # Utility functions and helpers
├── ui/
│   ├── __init__.py
│   ├── sidebar.py        # Sidebar UI component
│   ├── tab1.py           # Chat interface
│   ├── tab2.py           # Document management
│   └── streamlit_app.py  # Main application
├── scripts/              # Utility scripts
├── docs/                 # Document storage
├── temp/                 # Temporary files
├── db/                   # Vector database storage
├── .streamlit/           # Streamlit configuration
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .env                  # Environment variables
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

### Utils
The utils module provides:
- Helper functions for the main application

#### ⚠️ If you are using this code for the first time, you will need to put a document in the database. You can do it through the UI or using script/handle_documents.py



