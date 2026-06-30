import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from app.config import settings, has_llm_credentials, get_llm

logger = logging.getLogger("startup_advisor.agents.planner")

def run_planner(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Planner Agent: Analyzes the startup idea and establishes an outline 
    of points to research and validate.
    """
    idea = state["idea"]
    logger.info(f"Running Planner Agent for idea: '{idea[:50]}'")
    
    logs = list(state.get("logs") or [])
    logs.append("Planner Agent: Commencing analysis. Defining validation roadmap...")
    
    if not has_llm_credentials():
        # Dry run / fallback mock data
        mock_plan = (
            f"1. Competitor Identification: Identify digital fitness solutions targeting student demography.\n"
            f"2. Market Sizing: Calculate TAM based on student enrollment, SAM for English speakers, and SOM for local campuses.\n"
            f"3. Risk Diagnostics: Analyze student price sensitivity, app abandonment rate, and platform lock-in.\n"
            f"4. Stack Alignment: Recommend lightweight mobile framework (e.g., React Native) with low-overhead backend."
        )
        return {
            "plan": mock_plan,
            "current_agent": "planner",
            "logs": logs + ["Planner Agent: Formulated validation plan (Mock Fallback)."]
        }
        
    try:
        llm = get_llm(temperature=0.3)
        
        prompt = f"""
You are an expert Startup Venture Builder and Product Strategist (Planner Agent).
Your goal is to build a customized, step-by-step validation plan for the following startup idea:
Idea: "{idea}"

Determine:
1. What specific categories of competitors must be researched.
2. What target demographic assumptions need verification.
3. What key feasibility and unit economic risks should be scrutinized.
4. What core technical criteria must be evaluated for the MVP stack.

Provide a concise, professional roadmap of analysis points. Use Markdown.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        plan_content = response.content.strip()
        
        return {
            "plan": plan_content,
            "current_agent": "planner",
            "logs": logs + ["Planner Agent: Developed customized startup validation roadmap."]
        }
    except Exception as e:
        logger.error(f"Error in Planner Agent: {e}")
        mock_plan = (
            f"1. Competitor Identification: Identify digital fitness solutions targeting student demography.\n"
            f"2. Market Sizing: Calculate TAM based on student enrollment, SAM for English speakers, and SOM for local campuses.\n"
            f"3. Risk Diagnostics: Analyze student price sensitivity, app abandonment rate, and platform lock-in.\n"
            f"4. Stack Alignment: Recommend lightweight mobile framework (e.g., React Native) with low-overhead backend."
        )
        return {
            "plan": mock_plan,
            "current_agent": "planner",
            "logs": logs + [f"Planner Agent: Developed startup validation roadmap (parametric fallback: {e})."]
        }
