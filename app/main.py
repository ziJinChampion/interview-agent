from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import time
from fastapi.responses import HTMLResponse
from app.api import interview
from app.core.vector_store import vector_store_service
from app.core.logger import get_logger, log_startup, log_shutdown, log_success, log_error

# Get logger for this module
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize vector store on application startup."""
    try:
        log_startup("Interview Agent Application")
        logger.info("📚 Initializing vector store...")
        
        # Initialize vector store service
        vector_store = vector_store_service.initialize_vector_store()
        
        # Log vector store status
        if vector_store:
            collection = vector_store._collection
            count = collection.count()
            log_success(f"Vector store initialized successfully with {count} documents")
        else:
            logger.warning("⚠️ Vector store initialization failed")
            
        yield  # This is where the app runs
        
        log_shutdown("Interview Agent Application")
            
    except Exception as e:
        log_error(f"Error during startup: {e}")
        raise

app = FastAPI(
    title="Interview Agent", 
    description="AI-powered interview preparation system",
    lifespan=lifespan
)

# Serve static files (frontend)
frontend_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

app.include_router(interview.router)

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open(os.path.join(frontend_dir, "index.html"), "r") as f:
        return f.read()

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "vector_store": "initialized"}

@app.get("/logs")
def get_logs(level: str = "INFO", lines: int = 100):
    """Get recent logs from the log file."""
    try:
        with open('logs/app.log', 'r', encoding='utf-8') as f:
            log_lines = f.readlines()
        
        # Filter by level if specified
        if level.upper() != "ALL":
            log_lines = [line for line in log_lines if f" - {level.upper()} - " in line]
        
        # Get last N lines
        recent_logs = log_lines[-lines:] if lines > 0 else log_lines
        
        return {
            "logs": recent_logs,
            "total_lines": len(log_lines),
            "returned_lines": len(recent_logs),
            "level": level
        }
    except FileNotFoundError:
        return {"error": "Log file not found"}
    except Exception as e:
        return {"error": str(e)} 