#!/usr/bin/env python3
"""
Test script for vector store functionality
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.vector_store import VectorStoreService

def test_vector_store():
    """Test the vector store functionality."""
    print("Testing Vector Store Setup...")
    
    # Create vector store service with test paths
    docs_path = "../docs"  # Updated to match user's configuration
    persist_dir = "./db/chroma_db"
    
    service = VectorStoreService(
        docs_path=docs_path,
        persist_directory=persist_dir
    )
    
    try:
        # Test document loading
        print(f"Loading documents from: {docs_path}")
        documents = service.load_documents_from_directory()
        print(f"Loaded {len(documents)} documents")
        
        if documents:
            print("Sample document metadata:")
            for i, doc in enumerate(documents[:3]):
                print(f"  {i+1}. {doc.metadata.get('rel_path', 'unknown')} - {doc.metadata.get('category', 'unknown')}")
        
        # Test vector store initialization
        print("\nInitializing vector store...")
        vector_store = service.initialize_vector_store()
        
        if vector_store:
            collection = vector_store._collection
            count = collection.count()
            print(f"Vector store initialized successfully with {count} documents")
            
            # Test search functionality
            print("\nTesting search functionality...")
            test_query = "system design"
            results = service.search(test_query, k=3)
            print(f"Search results for '{test_query}':")
            for i, doc in enumerate(results):
                print(f"  {i+1}. {doc.metadata.get('filename', 'unknown')} - {doc.metadata.get('category', 'unknown')}")
                print(f"     Content preview: {doc.page_content[:100]}...")
        
        print("\n✅ Vector store test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during vector store test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vector_store() 