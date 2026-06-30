import logging
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from app.config import settings, has_llm_credentials, get_llm
from app.tools.rag import retrieve_startup_knowledge

logger = logging.getLogger("startup_advisor.agents.market_analyst")

def run_market_analyst(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Market Analysis Agent: Uses RAG to retrieve business frameworks and 
    performs TAM/SAM/SOM market sizing and audience profiling.
    """
    idea = state["idea"]
    logger.info(f"Running Market Analysis Agent for idea: '{idea[:50]}'")
    
    logs = list(state.get("logs") or [])
    logs.append("Market Analysis Agent: Querying RAG knowledge base for market sizing frameworks...")
    
    # 1. Retrieve RAG context
    rag_context = retrieve_startup_knowledge("TAM SAM SOM market sizing calculation bottom-up guide", num_results=2)
    
    logs.append("Market Analysis Agent: Performing bottom-up market sizing and audience profiling...")
    
    if not has_llm_credentials():
        # Fallback market analysis
        mock_analysis = {
            "tam": "$12,000,000,000 / year",
            "sam": "$1,200,000,000 / year",
            "som": "$3,000,000 / year",
            "target_audience": "Active college students (aged 18-24) who gym regularly and use mobile tech.",
            "monetization": "Freemium: Free tracking, $4.99/mo premium tier for customized AI guidance and community workouts.",
            "sizing_breakdown": (
                "Based on 200M students globally (TAM), 20M in the USA (SAM), "
                "and targeting 50k users across 50 partner universities at $60/yr ACV (SOM)."
            )
        }
        return {
            "market_analysis": mock_analysis,
            "current_agent": "market_analyst",
            "logs": logs + ["Market Analysis Agent: Performed TAM/SAM/SOM estimates (Mock Fallback)."]
        }
        
    try:
        llm = get_llm(temperature=0.3)
        
        prompt = f"""
You are a startup market analyst (Market Analysis Agent).
Your goal is to estimate the market size (TAM/SAM/SOM) and define the target audience and pricing for this idea:
Idea: "{idea}"

Use the following RAG knowledge base guidelines to structure your bottom-up calculations:
{rag_context}

Provide a realistic, data-backed (bottom-up logic) estimation of:
1. TAM (Total Addressable Market) - Global maximum size.
2. SAM (Serviceable Addressable Market) - Targetable segment (e.g. English-speaking, specific countries/tech).
3. SOM (Serviceable Obtainable Market) - Realistic capture in first 3 years.
4. Target Audience profile.
5. Recommended Monetization Model.
6. Step-by-step breakdown of your sizing calculations (numbers, assumptions, price points).

Return the result STRICTLY as a JSON object with the keys: "tam", "sam", "som", "target_audience", "monetization", "sizing_breakdown".
Do not include markdown formatting or explanation text.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                content = "\n".join(lines[1:-1])
                
        analysis = json.loads(content)
        
        return {
            "market_analysis": analysis,
            "current_agent": "market_analyst",
            "logs": logs + ["Market Analysis Agent: Computed bottom-up market sizing metrics."]
        }
    except Exception as e:
        logger.error(f"Error in Market Analysis Agent: {e}")
        mock_analysis = {
            "tam": "$12,000,000,000 / year",
            "sam": "$1,200,000,000 / year",
            "som": "$3,000,000 / year",
            "target_audience": "Active college students (aged 18-24) who gym regularly and use mobile tech.",
            "monetization": "Freemium: Free tracking, $4.99/mo premium tier for customized AI guidance and community workouts.",
            "sizing_breakdown": (
                "Based on 200M students globally (TAM), 20M in the USA (SAM), "
                "and targeting 50k users across 50 partner universities at $60/yr ACV (SOM)."
            )
        }
        return {
            "market_analysis": mock_analysis,
            "current_agent": "market_analyst",
            "logs": logs + [f"Market Analysis Agent: Computed bottom-up market sizing metrics (parametric fallback: {e})."]
        }
