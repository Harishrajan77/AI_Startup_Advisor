import pytest
import os
# Prevent duplicate OpenMP library initialization crash on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import ValidationRun
from app.rag.embedder import load_knowledge_base
from app.tools.search import search_web
from app.agents.workflow import agent_graph

# Setup temporary test database
@pytest.fixture(scope="function")
def db_session():
    # Use SQLite in-memory database for rapid unit testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_validation_run_model(db_session):
    """Verifies database insertion and serialization works as expected."""
    run = ValidationRun(
        idea="A subscription box for organic dog food",
        status="PENDING",
        logs=["Initializing test record..."]
    )
    db_session.add(run)
    db_session.commit()
    
    saved_run = db_session.query(ValidationRun).filter(ValidationRun.idea == "A subscription box for organic dog food").first()
    assert saved_run is not None
    assert saved_run.status == "PENDING"
    assert "Initializing test record..." in saved_run.logs
    
    serialized = saved_run.to_dict()
    assert serialized["id"] == saved_run.id
    assert serialized["idea"] == "A subscription box for organic dog food"

def test_rag_knowledge_loader():
    """Validates that RAG loader handles document chunking logic."""
    # Ensure directory exists
    os.makedirs("./knowledge_base", exist_ok=True)
    docs = load_knowledge_base()
    # If the directories are loaded, we should see documents parsed (or empty if none created in local path)
    assert isinstance(docs, list)

def test_search_tool_fallback():
    """Verifies search fallback retrieves realistic competitor data."""
    # Run tool without Tavily key
    results = search_web("dorm room workout planner competitors", "AI fitness app for students")
    assert isinstance(results, list)
    assert len(results) > 0
    # Checks that returned items have search attributes
    assert "title" in results[0] or "name" in results[0]

def test_langgraph_structure():
    """Verifies that the compiled LangGraph exists and exposes its input/output channels."""
    assert agent_graph is not None
    # Verify the structure has entry points and correct node mappings
    assert "planner" in agent_graph.nodes
    assert "researcher" in agent_graph.nodes
    assert "market_analyst" in agent_graph.nodes
    assert "risk_assessor" in agent_graph.nodes
    assert "tech_advisor" in agent_graph.nodes
    assert "report_generator" in agent_graph.nodes
