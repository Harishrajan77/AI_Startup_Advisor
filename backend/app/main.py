import logging
import os
# Prevent duplicate OpenMP library initialization crash on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import engine, Base
from app.api.routes import router as api_router
from app.rag.vector_store import get_vector_db

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("startup_advisor")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager handling startup & shutdown operations."""
    logger.info("Initializing application metadata...")
    
    # 1. Initialize SQL Database tables
    try:
        logger.info("Syncing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database synced successfully.")
    except Exception as e:
        logger.error(f"Failed to sync database: {e}")
        
    # 2. Build RAG Vector Index
    try:
        logger.info("Initializing vector store index...")
        db = get_vector_db()
        if db:
            logger.info("Vector store index loaded and ready.")
        else:
            logger.warning("Vector store database loading failed.")
    except Exception as e:
        logger.error(f"Error building/loading RAG index: {e}")
        
    yield
    
    logger.info("Shutting down application...")

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agentic AI Startup validation advisor powered by LangGraph, FastAPI, and FAISS RAG.",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS middleware to allow connection from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development; adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bind routes
app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "app": "AI Startup Advisor API",
        "status": "online",
        "description": "Multi-agent LangGraph workflow running on FastAPI."
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting uvicorn server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=False
    )
