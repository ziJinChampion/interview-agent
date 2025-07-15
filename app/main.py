from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
import sys
from fastapi.responses import HTMLResponse
from app.api import interview
from app.core.vector_store import vector_store_service

# Configure logging with multiple handlers
def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler (shows in terminal)
            logging.StreamHandler(sys.stdout),
            # File handler (saves to file)
            logging.FileHandler('logs/app.log', mode='a', encoding='utf-8'),
        ]
    )

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize vector store on application startup."""
    try:
        logger.info("🚀 Starting application...")
        logger.info("📚 Initializing vector store...")
        
        # Initialize vector store service
        vector_store = vector_store_service.initialize_vector_store()
        
        # Log vector store status
        if vector_store:
            collection = vector_store._collection
            count = collection.count()
            logger.info(f"✅ Vector store initialized successfully with {count} documents")
        else:
            logger.warning("⚠️ Vector store initialization failed")
            
        yield  # This is where the app runs
        
        logger.info("🛑 Shutting down application...")
            
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
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