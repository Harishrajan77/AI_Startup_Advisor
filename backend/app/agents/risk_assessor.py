import logging
import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from app.config import settings, has_llm_credentials, get_llm
from app.tools.rag import retrieve_startup_knowledge

logger = logging.getLogger("startup_advisor.agents.risk_assessor")

def run_risk_assessor(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Risk Assessment Agent: Evaluates barriers, conducts SWOT analysis, 
    and builds a risk mitigation matrix based on RAG knowledge files.
    """
    idea = state["idea"]
    logger.info(f"Running Risk Assessment Agent for idea: '{idea[:50]}'")
    
    logs = list(state.get("logs") or [])
    logs.append("Risk Assessment Agent: Fetching risk matrices and failure mode templates from RAG...")
    
    # 1. Retrieve RAG risk context
    rag_context = retrieve_startup_knowledge("SWOT analysis risk categories matrix mitigation", num_results=2)
    
    logs.append("Risk Assessment Agent: Executing SWOT diagnostic and risk prioritization...")
    
    if not has_llm_credentials():
        # Fallback risk assessment
        mock_risks = {
            "swot": {
                "strengths": ["Hyper-focused niche (students)", "Low operational cost starting out", "Gamified community features"],
                "weaknesses": ["Low starting budget", "High student churn during summers/graduation", "Platform dependence (App Store)"],
                "opportunities": ["Growth in university campus wellness programs", "Partnerships with campus gyms", "AI gym buddy micro-influencers"],
                "threats": ["Free competitors (Strava, Nike)", "Fast-follow copycats", "Change in school gym access policies"]
            },
            "matrix": [
                {
                    "risk_category": "Customer Retention (Market)",
                    "description": "Students abandoning the app after initial curiosity or during summer break.",
                    "probability": "High",
                    "impact": "High",
                    "mitigation": "Introduce vacation freeze modes, graduation community roll-overs, and summer challenges."
                },
                {
                    "risk_category": "API Costs (Financial/Technical)",
                    "description": "High API token expenses for continuous personalized AI routine generation.",
                    "probability": "Medium",
                    "impact": "Medium",
                    "mitigation": "Cache typical workout templates, use smaller model variants (e.g. Gemini Flash), rate-limit free tier."
                },
                {
                    "risk_category": "Student Privacy & Safety (Legal)",
                    "description": "Tracking student locations/routes and user-submitted data raises safety concerns.",
                    "probability": "Low",
                    "impact": "High",
                    "mitigation": "Enforce strict privacy controls, anonymize running paths near residence halls, comply with CCPA."
                }
            ]
        }
        return {
            "risks": mock_risks,
            "current_agent": "risk_assessor",
            "logs": logs + ["Risk Assessment Agent: Structured SWOT and risk matrix (Mock Fallback)."]
        }
        
    try:
        llm = get_llm(temperature=0.3)
        
        # Include competitor and market findings for context
        competitors_str = json.dumps(state.get("competitors") or [], indent=2)
        market_str = json.dumps(state.get("market_analysis") or {}, indent=2)
        
        prompt = f"""
You are a startup risk analyst and business auditor (Risk Assessment Agent).
Analyze the risks and generate a SWOT analysis and risk matrix for this idea:
Idea: "{idea}"

Context:
- Competitors: {competitors_str}
- Market Sizing & Price model: {market_str}

Use the RAG guidelines on risk mitigation and failure modes:
{rag_context}

Generate:
1. A SWOT analysis (Strengths, Weaknesses, Opportunities, Threats).
2. A Risk Matrix identifying the top 3-4 risks, specifying:
   - Category (e.g., Market, Technical, Financial, Legal/Regulatory)
   - Description of the risk
   - Probability (Low, Medium, High)
   - Impact (Low, Medium, High)
   - Actionable Mitigation Strategy

Return the result STRICTLY as a JSON object with the keys: "swot" (which contains "strengths", "weaknesses", "opportunities", "threats" as lists of strings) and "matrix" (which is a list of objects containing "risk_category", "description", "probability", "impact", "mitigation").
Do not include markdown formatting or explanation text.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                content = "\n".join(lines[1:-1])
                
        risks_data = json.loads(content)
        
        return {
            "risks": risks_data,
            "current_agent": "risk_assessor",
            "logs": logs + ["Risk Assessment Agent: Formulated SWOT profile and risk scoring matrix."]
        }
    except Exception as e:
        logger.error(f"Error in Risk Assessment Agent: {e}")
        mock_risks = {
            "swot": {
                "strengths": ["Hyper-focused niche (students)", "Low operational cost starting out", "Gamified community features"],
                "weaknesses": ["Low starting budget", "High student churn during summers/graduation", "Platform dependence (App Store)"],
                "opportunities": ["Growth in university campus wellness programs", "Partnerships with campus gyms", "AI gym buddy micro-influencers"],
                "threats": ["Free competitors (Strava, Nike)", "Fast-follow copycats", "Change in school gym access policies"]
            },
            "matrix": [
                {
                    "risk_category": "Customer Retention (Market)",
                    "description": "Students abandoning the app after initial curiosity or during summer break.",
                    "probability": "High",
                    "impact": "High",
                    "mitigation": "Introduce vacation freeze modes, graduation community roll-overs, and summer challenges."
                },
                {
                    "risk_category": "API Costs (Financial/Technical)",
                    "description": "High API token expenses for continuous personalized AI routine generation.",
                    "probability": "Medium",
                    "impact": "Medium",
                    "mitigation": "Cache typical workout templates, use smaller model variants (e.g. Gemini Flash), rate-limit free tier."
                },
                {
                    "risk_category": "Student Privacy & Safety (Legal)",
                    "description": "Tracking student locations/routes and user-submitted data raises safety concerns.",
                    "probability": "Low",
                    "impact": "High",
                    "mitigation": "Enforce strict privacy controls, anonymize running paths near residence halls, comply with CCPA."
                }
            ]
        }
        return {
            "risks": mock_risks,
            "current_agent": "risk_assessor",
            "logs": logs + [f"Risk Assessment Agent: Formulated SWOT profile and risk scoring matrix (parametric fallback: {e})."]
        }
