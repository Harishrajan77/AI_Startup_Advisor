import os
import logging
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.rag.embedder import get_embeddings, build_vector_store
from app.config import settings

logger = logging.getLogger("startup_advisor.vector_store")
logger.setLevel(logging.INFO)

# Global index instance
_vector_db = None

def get_vector_db():
    """Lazy load or initialize the FAISS vector database."""
    global _vector_db
    if _vector_db is not None:
        return _vector_db
        
    embeddings = get_embeddings()
    index_path = settings.VECTOR_STORE_DIR
    
    # Check if the FAISS index files exist
    index_file = os.path.join(index_path, "index.faiss")
    meta_file = os.path.join(index_path, "index.pkl")
    
    if os.path.exists(index_file) and os.path.exists(meta_file):
        try:
            logger.info(f"Loading existing FAISS index from {index_path}...")
            # FAISS allow_dangerous_deserialization is safe since we compile it locally
            loaded_db = FAISS.load_local(
                index_path, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            # Verify dimension compatibility
            sample_dim = len(embeddings.embed_query("test"))
            if loaded_db.index.d != sample_dim:
                raise ValueError(f"FAISS index dimension mismatch: Loaded index has {loaded_db.index.d} dims, current embeddings have {sample_dim} dims.")
            
            _vector_db = loaded_db
            return _vector_db
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}. Rebuilding index...")
            
    # Build a new index if it doesn't exist or failed to load
    _vector_db = build_vector_store()
    return _vector_db

def query_knowledge_base(query: str, k: int = 3) -> List[Document]:
    """Retrieve top k relevant documents matching the query."""
    db = get_vector_db()
    if not db:
        logger.warning("Vector database is unavailable. Returning empty result list.")
        return []
        
    try:
        results = db.similarity_search(query, k=k)
        logger.info(f"RAG query: '{query}' returned {len(results)} matches.")
        return results
    except Exception as e:
        logger.error(f"Error querying FAISS index: {e}")
        return []
