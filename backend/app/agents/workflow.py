import logging
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# Import agent nodes
from app.agents.planner import run_planner
from app.agents.researcher import run_researcher
from app.agents.market_analyst import run_market_analyst
from app.agents.risk_assessor import run_risk_assessor
from app.agents.tech_advisor import run_tech_advisor
from app.agents.report_generator import run_report_generator

logger = logging.getLogger("startup_advisor.workflow")

# Define the state schema shared across all nodes
class AgentState(TypedDict):
    idea: str
    plan: str
    competitors: List[Dict[str, Any]]
    market_analysis: Dict[str, Any]
    risks: Dict[str, Any]
    tech_stack: Dict[str, Any]
    report: str
    logs: List[str]
    current_agent: str

def create_workflow():
    """Builds and compiles the multi-agent LangGraph workflow."""
    logger.info("Initializing LangGraph StateGraph...")
    
    # 1. Instantiate the state graph
    workflow = StateGraph(AgentState)
    
    # 2. Add all agent nodes to the graph
    workflow.add_node("planner", run_planner)
    workflow.add_node("researcher", run_researcher)
    workflow.add_node("market_analyst", run_market_analyst)
    workflow.add_node("risk_assessor", run_risk_assessor)
    workflow.add_node("tech_advisor", run_tech_advisor)
    workflow.add_node("report_generator", run_report_generator)
    
    # 3. Establish flow transitions
    workflow.set_entry_point("planner")
    
    # Linear pipeline for structured startup assessment
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "market_analyst")
    workflow.add_edge("market_analyst", "risk_assessor")
    workflow.add_edge("risk_assessor", "tech_advisor")
    workflow.add_edge("tech_advisor", "report_generator")
    workflow.add_edge("report_generator", END)
    
    # 4. Compile the graph
    compiled_graph = workflow.compile()
    logger.info("LangGraph workflow successfully compiled.")
    return compiled_graph

# Compile single graph instance for app use
agent_graph = create_workflow()
