# interview.py - API routes for interview agent

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Literal, Optional
from app.llm.chain import ask_openai, search_documents
from app.core.vector_store import vector_store_service
import os
import logging

router = APIRouter()

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    

class ChatRequest(BaseModel):
    messages: List[Message]
    job_tile: str
    job_description: str
    user_resume: str

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    category: Optional[str] = None

@router.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        ask_openai(request.messages, request.job_tile, request.job_description, request.user_resume),
        media_type="text/event-stream"
    )

@router.post("/search")
async def search_docs(request: SearchRequest):
    """Search for relevant documents."""
    try:
        results = search_documents(
            query=request.query,
            k=request.k,
            category=request.category
        )
        
        # Format results for response
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", ""),
                "category": doc.metadata.get("category", ""),
                "filename": doc.metadata.get("filename", ""),
            })
            
        return {
            "query": request.query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/vector-store/status")
async def get_vector_store_status():
    """Get vector store status and statistics."""
    try:
        vector_store = vector_store_service.get_vector_store()
        collection = vector_store._collection
        count = collection.count()
        
        return {
            "status": "active",
            "document_count": count,
            "persist_directory": vector_store_service.persist_directory,
            "docs_path": vector_store_service.docs_path
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/vector-store/refresh")
async def refresh_vector_store():
    """Refresh the vector store by reloading all documents."""
    try:
        vector_store_service.refresh_vector_store()
        return {"status": "success", "message": "Vector store refreshed successfully"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/vector-store/debug")
async def debug_vector_store():
    """Debug vector store status and configuration."""
    try:
        # Call the debug function
        vector_store_service.debug_vector_store_status()
        
        # Get additional information
        vector_store = vector_store_service.get_vector_store()
        collection = vector_store._collection
        count = collection.count()
        
        return {
            "status": "debug_completed",
            "document_count": count,
            "docs_path": vector_store_service.docs_path,
            "persist_directory": vector_store_service.persist_directory,
            "message": "Check the logs for detailed debug information"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/vector-store/force-refresh")
async def force_refresh_vector_store():
    """Force refresh the vector store by completely removing and recreating it."""
    try:
        logger.info("Force refreshing vector store...")
        
        # Remove the persist directory completely
        if os.path.exists(vector_store_service.persist_directory):
            import shutil
            shutil.rmtree(vector_store_service.persist_directory)
            logger.info("Removed existing persist directory")
        
        # Reset the vector store instance
        vector_store_service.vector_store = None
        
        # Reinitialize
        vector_store = vector_store_service.initialize_vector_store()
        
        if vector_store:
            collection = vector_store._collection
            count = collection.count()
            return {
                "status": "success", 
                "message": f"Vector store force refreshed successfully with {count} documents"
            }
        else:
            return {"status": "error", "message": "Failed to initialize vector store"}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}

# TODO: Define interview-related API routes here 