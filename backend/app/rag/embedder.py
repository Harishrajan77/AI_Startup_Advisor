import os
import logging
from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import settings

logger = logging.getLogger("startup_advisor.embedder")
logger.setLevel(logging.INFO)

def get_embeddings():
    """Get the appropriate embedding model based on settings."""
    if settings.MODEL_PROVIDER.lower() == "groq":
        try:
            logger.info("Initializing HuggingFace local embeddings (all-MiniLM-L6-v2) for Groq pipeline...")
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace local embeddings: {e}. Falling back to FakeEmbeddings.")
            return FakeEmbeddings(size=384)
            
    # Default is gemini
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set! RAG will use FakeEmbeddings for dry-run/mock execution.")
        return FakeEmbeddings(size=768)
    
    try:
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GEMINI_API_KEY
        )
    except Exception as e:
        logger.error(f"Failed to initialize Google GenAI Embeddings: {e}. Falling back to FakeEmbeddings.")
        return FakeEmbeddings(size=768)

def load_knowledge_base() -> List[Document]:
    """Reads markdown files from knowledge base directory and creates Document objects."""
    docs = []
    kb_dir = settings.KNOWLEDGE_BASE_DIR
    
    if not os.path.exists(kb_dir):
        logger.warning(f"Knowledge base directory '{kb_dir}' does not exist. Creating empty vector store.")
        # Create directory
        os.makedirs(kb_dir, exist_ok=True)
        return docs
        
    for filename in os.listdir(kb_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(kb_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Split files by double newlines or headers to create logical chunks
                # This simple markdown splitter is extremely clean and transparent
                chunks = content.split("\n## ")
                
                # First chunk (before the first ##) is usually the title/intro
                if chunks[0].strip():
                    docs.append(Document(
                        page_content=chunks[0].strip(),
                        metadata={"source": filename, "chunk": 0}
                    ))
                    
                for i, chunk in enumerate(chunks[1:], start=1):
                    if chunk.strip():
                        # Prepend '## ' back to preserve markdown structure for context
                        docs.append(Document(
                            page_content=f"## {chunk.strip()}",
                            metadata={"source": filename, "chunk": i}
                        ))
                logger.info(f"Loaded and chunked {filename} into {len(chunks)} fragments.")
            except Exception as e:
                logger.error(f"Error loading knowledge base file {filename}: {e}")
                
    return docs

def build_vector_store():
    """Builds a FAISS vector index from knowledge base files and saves it locally."""
    embeddings = get_embeddings()
    docs = load_knowledge_base()
    
    if not docs:
        logger.warning("No knowledge base documents found. Indexing placeholder document.")
        docs = [Document(page_content="AI Startup Advisor vector store is active.", metadata={"source": "system"})]
        
    try:
        logger.info(f"Building FAISS vector index with {len(docs)} documents...")
        db = FAISS.from_documents(docs, embeddings)
        
        # Save FAISS index locally
        os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
        db.save_local(settings.VECTOR_STORE_DIR)
        logger.info(f"FAISS vector store successfully saved to '{settings.VECTOR_STORE_DIR}'")
        return db
    except Exception as e:
        logger.error(f"Failed to build FAISS vector store: {e}")
        return None
