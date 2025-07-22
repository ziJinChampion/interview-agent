# chain.py - Langchain integration
from openai import OpenAI, AsyncOpenAI
import os
import time
from dotenv import load_dotenv
from app.llm.prompts import question_prompt, classification_prompt, feedback_prompt
from typing import Generator
from app.core.vector_store import vector_store_service
from app.core.logger import get_logger
import asyncio
import aiohttp

load_dotenv()

API_KEY = os.getenv("API_KEY")
GENERAL_MODEL = os.getenv("GENERAL_MODEL")
GENERAL_MODEL_BASE_URL = os.getenv("GENERAL_MODEL_BASE_URL")
client = OpenAI(api_key=API_KEY, base_url=GENERAL_MODEL_BASE_URL)
async_client = AsyncOpenAI(api_key=API_KEY, base_url=GENERAL_MODEL_BASE_URL)

logger = get_logger("llm.chain")

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


async def call_llm_async(messages: list) -> str:
    """Async version of call_llm for parallel execution."""
    try:
        response = await async_client.chat.completions.create(
            model=GENERAL_MODEL,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "Failed to call LLM"

async def chain_ask_openai(messages: list, job_tile: str, job_description: str, user_resume: str):
    knowledge_points = ""
    classification_messages = [{"role": "system", "content": classification_prompt}]
    feedback_messages = [{"role": "system", "content": feedback_prompt}]
    feedback = None
    
    if len(messages) == 1:
        first_message = [{"role": "user", "content": job_tile + job_description + user_resume}] 
        logger.info(f"User first message: {first_message}")
        knowledge_points = call_llm(classification_messages + first_message)
    else:
        logger.info(f"User message: {messages[-1].content}")
        
        task1 = asyncio.create_task(call_llm_async(classification_messages + [{"role": "user", "content": messages[-1].content}]))
        task2 = asyncio.create_task(call_llm_async(feedback_messages + [{"role": "user", "content": messages[-1].content}]))
        
        knowledge_points_result, feedback_result = await asyncio.gather(task1, task2)
        knowledge_points = knowledge_points_result
        feedback = feedback_result
    
    logger.info(f"Knowledge points: {knowledge_points}")
    logger.info(f"Feedback: {feedback}")

    retriever = get_document_retriever(k=5)
    search_results = retriever.get_relevant_documents(knowledge_points)
    formatted_results = format_search_results(search_results)
    logger.info(f"refer questions: {formatted_results}")
    
    question_prompt_template = question_prompt.format(example_questions=formatted_results, knowledge_points=knowledge_points, feedback=feedback)
    messages = [{"role": "system", "content": question_prompt_template}]
    logger.info(f"Generate question template successfully")
    
    return call_llm_streamly(messages)

def call_llm(messages: list) -> Generator[str, None, None]:
    try:
        response = client.chat.completions.create(
            model=GENERAL_MODEL,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "Failed to call LLM"

def call_llm_streamly(messages: list) -> Generator[str, None, None]:
    try:
        response = client.chat.completions.create(
            model=GENERAL_MODEL,
            messages=messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield "Failed to call LLM"

# Helper function to search documents
def search_documents(query: str, k: int = 5, category: str = None):
    """Search for relevant documents using the vector store."""
    filter_dict = {"category": category} if category else None
    return vector_store_service.search(query, k=k, filter_dict=filter_dict)

# Helper function to get retriever for RAG
def get_document_retriever(k: int = 5):
    """Get a retriever for use in RAG chains."""
    return vector_store_service.get_retriever({"k": k})