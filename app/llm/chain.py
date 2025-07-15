# chain.py - Langchain integration
from openai import OpenAI
import os
from dotenv import load_dotenv
from app.llm.prompts import Role_prompt
from typing import Generator
from app.core.vector_store import vector_store_service

load_dotenv()

API_KEY = os.getenv("API_KEY")
GENERAL_MODEL = os.getenv("GENERAL_MODEL")
GENERAL_MODEL_BASE_URL = os.getenv("GENERAL_MODEL_BASE_URL")
client = OpenAI(api_key=API_KEY, base_url=GENERAL_MODEL_BASE_URL)

def format_search_results(search_results: list) -> str:
    """Format search results as a string with indices and content."""
    if not search_results:
        return "No relevant documents found."
    
    formatted_results = []
    for i, result in enumerate(search_results, 1):
        # Extract content from the result (adjust based on your result structure)
        content = result.get('content', str(result)) if isinstance(result, dict) else str(result)
        formatted_results.append(f"{i}. {content}")
    
    return "\n".join(formatted_results)


# Accepts a list of messages (conversation history)
def ask_openai(messages: list, job_tile: str, job_description: str, user_resume: str) -> Generator[str, None, None]:
    if len(messages) == 1:
        search_results = search_documents(query=job_description, k=5)
        formatted_results = format_search_results(search_results)
        Role_prompt_template = Role_prompt.format(job_tile=job_tile, job_description=job_description, example_questions=formatted_results, user_resume=user_resume)
        messages = [{"role": "system", "content": Role_prompt_template}] + messages
    
    try:
        response = client.chat.completions.create(
            model=GENERAL_MODEL,
            messages=messages,
            stream=True
        )
        
        # Stream the response chunks
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        print(f"LLM Error: {e}")
        yield "Sorry, I encountered an error. Please try again later."

# Helper function to search documents
def search_documents(query: str, k: int = 5, category: str = None):
    """Search for relevant documents using the vector store."""
    filter_dict = {"category": category} if category else None
    return vector_store_service.search(query, k=k, filter_dict=filter_dict)

# Helper function to get retriever for RAG
def get_document_retriever(k: int = 5):
    """Get a retriever for use in RAG chains."""
    return vector_store_service.get_retriever({"k": k})