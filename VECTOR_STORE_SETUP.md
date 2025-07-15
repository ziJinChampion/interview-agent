# Vector Store Setup Guide

This guide explains how to set up and use the Chroma vector database for document storage and retrieval in your interview agent application.

## Overview

The vector store automatically loads documents from `/app/docs` on application startup and provides semantic search capabilities for RAG (Retrieval-Augmented Generation) applications.

## Features

- **Automatic Document Loading**: Recursively loads documents from the docs directory
- **Smart Text Splitting**: Splits large documents into manageable chunks
- **Metadata Preservation**: Maintains document metadata (source, category, filename)
- **Persistence**: Saves vector embeddings to disk for fast reloading
- **Search API**: Provides similarity search with filtering capabilities
- **RAG Integration**: Ready-to-use retrievers for LangChain chains

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Make sure you have the following environment variables set:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Document Structure

Place your documents in `/app/docs` with the following structure:

```
app/docs/
├── system-design/
│   ├── microservices.md
│   └── scalability.md
├── java/
│   ├── spring-boot.md
│   └── multithreading.md
├── database/
│   ├── sql.md
│   └── nosql.md
└── home.md
```

### 4. Supported File Types

The vector store supports the following file extensions:
- `.md` - Markdown files
- `.txt` - Text files
- `.py` - Python files
- `.js` - JavaScript files
- `.ts` - TypeScript files
- `.java` - Java files
- `.cpp` - C++ files
- `.c` - C files
- `.h` - Header files

## Usage

### Application Startup

The vector store automatically initializes when your FastAPI application starts:

```python
# In app/main.py
@asynccontextmanager
async def lifespan():
    vector_store = vector_store_service.initialize_vector_store()
```

### Basic Search

```python
from app.core.vector_store import vector_store_service

# Search for documents
results = vector_store_service.search("system design patterns", k=5)

# Search with category filter
results = vector_store_service.search(
    "microservices", 
    k=3, 
    filter_dict={"category": "system-design"}
)
```

### Using in LLM Chains

```python
from app.llm.chain import get_document_retriever
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Get retriever
retriever = get_document_retriever(k=5)

# Create QA chain
llm = ChatOpenAI()
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# Query
response = qa_chain.run("What are microservices?")
```

### API Endpoints

The application provides several API endpoints for vector store operations:

#### Search Documents
```bash
POST /search
{
    "query": "system design",
    "k": 5,
    "category": "system-design"
}
```

#### Get Vector Store Status
```bash
GET /vector-store/status
```

#### Refresh Vector Store
```bash
POST /vector-store/refresh
```

## Configuration

### Vector Store Service Configuration

You can customize the vector store behavior by modifying the `VectorStoreService` class:

```python
# In app/core/vector_store.py
class VectorStoreService:
    def __init__(self, 
                 docs_path: str = "/app/docs",
                 persist_directory: str = "../db/chroma_db"):
        # Configuration options
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # Size of each chunk
            chunk_overlap=200,     # Overlap between chunks
            length_function=len,
        )
```

### Embedding Model

The default embedding model is OpenAI's text-embedding-ada-002. You can change this by modifying the embeddings initialization:

```python
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Use local embeddings
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
```

## Testing

Run the test script to verify your setup:

```bash
python test_vector_store.py
```

This will:
1. Load documents from `/app/docs`
2. Initialize the vector store
3. Test search functionality
4. Display results

## Troubleshooting

### Common Issues

1. **No documents loaded**: Check that `/app/docs` exists and contains supported file types
2. **API key error**: Ensure `OPENAI_API_KEY` is set correctly
3. **Permission errors**: Make sure the application has read access to the docs directory
4. **Memory issues**: Reduce `chunk_size` in the text splitter for large documents

### Debugging

Enable debug logging by modifying the logging level in `app/main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Refreshing Vector Store

If you add new documents, you can refresh the vector store:

```python
# Programmatically
vector_store_service.refresh_vector_store()

# Via API
curl -X POST http://localhost:8000/vector-store/refresh
```

## Performance Tips

1. **Chunk Size**: Adjust chunk size based on your document types (1000-2000 characters works well)
2. **Overlap**: Use 10-20% overlap for better context preservation
3. **Batch Processing**: For large document collections, consider batch processing
4. **Caching**: The vector store persists to disk, so subsequent startups are faster

## Advanced Usage

### Custom Document Processing

You can extend the document loading to handle custom file types:

```python
def load_custom_documents(self):
    # Add custom document processing logic
    pass
```

### Custom Embeddings

Implement custom embedding functions:

```python
class CustomEmbeddings:
    def embed_documents(self, texts):
        # Custom embedding logic
        pass
    
    def embed_query(self, text):
        # Custom query embedding
        pass
```

### Metadata Filtering

Use metadata filters for targeted searches:

```python
# Filter by multiple criteria
filter_dict = {
    "category": "system-design",
    "filename": "microservices.md"
}
results = vector_store_service.search("scalability", filter_dict=filter_dict)
``` 