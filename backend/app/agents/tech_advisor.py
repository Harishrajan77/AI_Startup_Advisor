import logging
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from app.config import settings, has_llm_credentials, get_llm
from app.tools.rag import retrieve_startup_knowledge

logger = logging.getLogger("startup_advisor.agents.tech_advisor")

def run_tech_advisor(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Technology Advisor Agent: Proposes tech stack recommendations, 
    infrastructure costs, and MVP scopes using RAG guidelines.
    """
    idea = state["idea"]
    logger.info(f"Running Tech Advisor Agent for idea: '{idea[:50]}'")
    
    logs = list(state.get("logs") or [])
    logs.append("Technology Advisor Agent: Querying RAG for tech stack benchmarks and cost structures...")
    
    # 1. Retrieve RAG tech context
    rag_context = retrieve_startup_knowledge("tech stack selection database MVP scope hosting costs", num_results=2)
    
    logs.append("Technology Advisor Agent: Structuring architecture design and MVP features...")
    
    if not has_llm_credentials():
        # Fallback tech advisor data
        mock_tech = {
            "frontend": "React Native (Expo) - allows rapid development of cross-platform apps using JavaScript/TypeScript.",
            "backend": "FastAPI (Python) - lightweight, asynchronous, perfect for serving AI models and logic.",
            "database": "PostgreSQL (Supabase) - manages user accounts and logs; provides serverless real-time data sync.",
            "infrastructure_hosting": "Vercel (frontend landing page), Render (FastAPI hosting), Supabase Cloud (DB).",
            "mvp_features": [
                "User sign-up & campus affiliation verification.",
                "Custom AI workout generator (based on equipment/time).",
                "Workout logging & progress calendar.",
                "Basic campus leaderboard/feed."
            ],
            "cost_estimate": "~$15 to $35/month (Vercel Free, Render Hobby DB/API, Supabase Free tier, $5-15 in LLM APIs)",
            "justification": (
                "Using React Native (Expo) allows a single developer to target iOS and Android. "
                "FastAPI is the standard for Python-based LLM middleware. Supabase cuts auth/DB setup times to zero."
            )
        }
        return {
            "tech_stack": mock_tech,
            "current_agent": "tech_advisor",
            "logs": logs + ["Technology Advisor Agent: Formulated architecture and MVP scope (Mock Fallback)."]
        }
        
    try:
        llm = get_llm(temperature=0.2)
        
        # Include competitor and market findings for context
        competitors_str = json.dumps(state.get("competitors") or [], indent=2)
        market_str = json.dumps(state.get("market_analysis") or {}, indent=2)
        
        prompt = f"""
You are a fractional CTO and solutions architect (Technology Advisor Agent).
Recommend a practical, cost-effective tech stack and MVP scope for this idea:
Idea: "{idea}"

Context:
- Competitors: {competitors_str}
- Market Sizing: {market_str}

Use the RAG guidelines on tech stack selection:
{rag_context}

Provide recommendations for:
1. Frontend framework (Web/Mobile cross-platform).
2. Backend API framework (and vector database if AI-enabled).
3. Primary Database choice.
4. Infrastructure hosting and deployment strategy.
5. MoSCoW MVP Feature scope (Must-have list of 3-4 features).
6. Estimated monthly hosting and API billing costs for the first 1,000 active users.
7. Technical Justification for these choices.

Return the result STRICTLY as a JSON object with the keys: "frontend", "backend", "database", "infrastructure_hosting", "mvp_features" (list of strings), "cost_estimate", "justification".
Do not include markdown formatting or explanation text.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                content = "\n".join(lines[1:-1])
                
        tech_data = json.loads(content)
        
        return {
            "tech_stack": tech_data,
            "current_agent": "tech_advisor",
            "logs": logs + ["Technology Advisor Agent: Outlined development stack and MVP scope."]
        }
    except Exception as e:
        logger.error(f"Error in Tech Advisor Agent: {e}")
        mock_tech = {
            "frontend": "React Native (Expo) - allows rapid development of cross-platform apps using JavaScript/TypeScript.",
            "backend": "FastAPI (Python) - lightweight, asynchronous, perfect for serving AI models and logic.",
            "database": "PostgreSQL (Supabase) - manages user accounts and logs; provides serverless real-time data sync.",
            "infrastructure_hosting": "Vercel (frontend landing page), Render (FastAPI hosting), Supabase Cloud (DB).",
            "mvp_features": [
                "User sign-up & campus affiliation verification.",
                "Custom AI workout generator (based on equipment/time).",
                "Workout logging & progress calendar.",
                "Basic campus leaderboard/feed."
            ],
            "cost_estimate": "~$15 to $35/month (Vercel Free, Render Hobby DB/API, Supabase Free tier, $5-15 in LLM APIs)",
            "justification": (
                "Using React Native (Expo) allows a single developer to target iOS and Android. "
                "FastAPI is the standard for Python-based LLM middleware. Supabase cuts auth/DB setup times to zero."
            )
        }
        return {
            "tech_stack": mock_tech,
            "current_agent": "tech_advisor",
            "logs": logs + [f"Technology Advisor Agent: Outlined development stack and MVP scope (parametric fallback: {e})."]
        }
