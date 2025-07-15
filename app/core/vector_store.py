import os
import glob
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
import logging

load_dotenv()

logger = logging.getLogger(__name__)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
print("EMBEDDING_MODEL: ", EMBEDDING_MODEL)
class VectorStoreService:
    def __init__(self, docs_path: str = "app/docs", persist_directory: str = "app/db/chroma_db"):
        self.docs_path = docs_path
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store: Optional[Chroma] = None
        
    def load_documents_from_directory(self) -> List[Document]:
        """Load all documents from the docs directory recursively."""
        documents = []
        docs_path = Path(self.docs_path)
        
        if not docs_path.exists():
            logger.warning(f"Docs directory {self.docs_path} does not exist")
            return documents
            
        # Supported file extensions
        supported_extensions = ['*.md', '*.txt', '*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.h']
        
        for extension in supported_extensions:
            pattern = str(docs_path / "**" / extension)
            files = glob.glob(pattern, recursive=True)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Create relative path for metadata
                    rel_path = os.path.relpath(file_path, self.docs_path)
                    
                    # Extract category from path
                    path_parts = rel_path.split(os.sep)
                    category = path_parts[0] if len(path_parts) > 1 else "root"
                    
                    document = Document(
                        page_content=content,
                        metadata={
                            "source": file_path,
                            "category": category,
                            "filename": os.path.basename(file_path),
                            "rel_path": rel_path
                        }
                    )
                    documents.append(document)
                    logger.info(f"Loaded document: {rel_path}")
                    
                except Exception as e:
                    logger.error(f"Error loading document {file_path}: {e}")
                    
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for better retrieval."""
        if not documents:
            return []
            
        split_docs = []
        for doc in documents:
            try:
                splits = self.text_splitter.split_documents([doc])
                for i, split in enumerate(splits):
                    split.metadata.update({
                        "chunk_index": i,
                        "total_chunks": len(splits)
                    })
                split_docs.extend(splits)
            except Exception as e:
                logger.error(f"Error splitting document {doc.metadata.get('source', 'unknown')}: {e}")
                
        logger.info(f"Documents split into {len(split_docs)} chunks")
        return split_docs
    
    def debug_vector_store_status(self):
        """Debug function to check vector store status."""
        logger.info("=== Vector Store Debug Information ===")
        logger.info(f"Docs path: {self.docs_path}")
        logger.info(f"Persist directory: {self.persist_directory}")
        
        # Check if docs directory exists
        docs_exists = os.path.exists(self.docs_path)
        logger.info(f"Docs directory exists: {docs_exists}")
        
        if docs_exists:
            docs_path = Path(self.docs_path)
            # Count files by extension
            file_counts = {}
            supported_extensions = ['*.md', '*.txt', '*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.h']
            
            for extension in supported_extensions:
                pattern = str(docs_path / "**" / extension)
                files = glob.glob(pattern, recursive=True)
                file_counts[extension] = len(files)
            
            logger.info(f"Files found by extension: {file_counts}")
            total_files = sum(file_counts.values())
            logger.info(f"Total supported files: {total_files}")
        
        # Check persist directory
        persist_exists = os.path.exists(self.persist_directory)
        logger.info(f"Persist directory exists: {persist_exists}")
        
        if persist_exists:
            # List contents of persist directory
            try:
                contents = os.listdir(self.persist_directory)
                logger.info(f"Persist directory contents: {contents}")
                
                # Check for Chroma database files
                chroma_files = ['chroma.sqlite3', 'chroma.sqlite3-shm', 'chroma.sqlite3-wal']
                for file in chroma_files:
                    file_path = os.path.join(self.persist_directory, file)
                    exists = os.path.exists(file_path)
                    logger.info(f"Chroma file {file}: {exists}")
                    
            except Exception as e:
                logger.error(f"Error reading persist directory: {e}")
        
        logger.info("=== End Debug Information ===")

    def initialize_vector_store(self) -> Chroma:
        """Initialize the vector store with documents."""
        try:
            # Debug current status
            self.debug_vector_store_status()
            
            # Check if vector store already exists and is valid
            if os.path.exists(self.persist_directory):
                # Check if it's a valid Chroma database by looking for required files
                chroma_files = ['chroma.sqlite3', 'chroma.sqlite3-shm', 'chroma.sqlite3-wal']
                has_chroma_files = any(os.path.exists(os.path.join(self.persist_directory, f)) for f in chroma_files)
                
                if has_chroma_files:
                    try:
                        logger.info("Loading existing vector store...")
                        self.vector_store = Chroma(
                            persist_directory=self.persist_directory,
                            embedding_function=self.embeddings
                        )
                        
                        # Verify the collection has documents
                        collection = self.vector_store._collection
                        count = collection.count()
                        
                        if count > 0:
                            logger.info(f"Existing vector store loaded successfully with {count} documents")
                            return self.vector_store
                        else:
                            logger.warning("Existing vector store is empty, recreating...")
                            # Remove empty database
                            import shutil
                            shutil.rmtree(self.persist_directory)
                    except Exception as e:
                        logger.warning(f"Error loading existing vector store: {e}. Recreating...")
                        # Remove corrupted database
                        import shutil
                        shutil.rmtree(self.persist_directory)
                else:
                    logger.info("Persist directory exists but is not a valid Chroma database. Recreating...")
                    # Remove invalid directory
                    import shutil
                    shutil.rmtree(self.persist_directory)
            
            # Load and process documents
            logger.info("Loading documents from directory...")
            documents = self.load_documents_from_directory()
            
            if not documents:
                logger.warning("No documents found. Creating empty vector store.")
                # Create persist directory if it doesn't exist
                os.makedirs(self.persist_directory, exist_ok=True)
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                return self.vector_store
            
            logger.info("Splitting documents into chunks...")
            split_documents = self.split_documents(documents)
            
            logger.info("Creating vector store...")
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.vector_store = Chroma.from_documents(
                documents=split_documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            logger.info(f"Vector store created successfully with {len(split_documents)} chunks")
            
            return self.vector_store
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def get_vector_store(self) -> Chroma:
        """Get the vector store instance."""
        if self.vector_store is None:
            self.vector_store = self.initialize_vector_store()
        return self.vector_store
    
    def search(self, query: str, k: int = 5, filter_dict: Optional[dict] = None) -> List[Document]:
        """Search for similar documents."""
        vector_store = self.get_vector_store()
        return vector_store.similarity_search(query, k=k, filter=filter_dict)
    
    def search_with_scores(self, query: str, k: int = 5, filter_dict: Optional[dict] = None):
        """Search for similar documents with similarity scores."""
        vector_store = self.get_vector_store()
        return vector_store.similarity_search_with_score(query, k=k, filter=filter_dict)
    
    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """Get a retriever for use in chains."""
        vector_store = self.get_vector_store()
        return vector_store.as_retriever(search_kwargs=search_kwargs or {"k": 5})
    
    def refresh_vector_store(self):
        """Refresh the vector store by reloading all documents."""
        logger.info("Refreshing vector store...")
        # Remove existing vector store
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)
        
        # Reinitialize
        self.vector_store = None
        return self.initialize_vector_store()

# Global instance
vector_store_service = VectorStoreService() 