import logging
from app.rag.vector_store import query_knowledge_base

logger = logging.getLogger("startup_advisor.tools.rag")
logger.setLevel(logging.INFO)

def retrieve_startup_knowledge(query: str, num_results: int = 2) -> str:
    """
    Search the RAG knowledge base for startup frameworks, market models, 
    and pricing recommendations.
    """
    logger.info(f"Retrieving startup knowledge for query: '{query}'")
    docs = query_knowledge_base(query, k=num_results)
    
    if not docs:
        return "No relevant startup advice found in the internal knowledge base."
        
    formatted_docs = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        formatted_docs.append(
            f"--- RAG Knowledge Source {i} (Document: {source}) ---\n"
            f"{doc.page_content.strip()}\n"
        )
        
    return "\n".join(formatted_docs)
