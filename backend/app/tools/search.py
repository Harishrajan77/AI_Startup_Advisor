import requests
import json
import logging
from typing import List, Dict, Any
from app.config import settings, has_llm_credentials, get_llm
from langchain_core.messages import HumanMessage

logger = logging.getLogger("startup_advisor.search")
logger.setLevel(logging.INFO)

def _search_tavily(query: str) -> List[Dict[str, Any]]:
    """Query the Tavily Search API directly via POST request."""
    if not settings.TAVILY_API_KEY:
        raise ValueError("Tavily API key is missing.")
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "max_results": 4
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    results = []
    for result in data.get("results", []):
        results.append({
            "title": result.get("title", "No Title"),
            "url": result.get("url", ""),
            "content": result.get("content", "")
        })
    return results

def _search_fallback_gemini(query: str, idea: str) -> List[Dict[str, Any]]:
    """Fallback search using LLM to retrieve competitor details based on parametric knowledge."""
    logger.info("Using LLM parametric search fallback for competitor discovery.")
    if not has_llm_credentials():
        logger.warning("No LLM credentials found. Returning static mock competitor results.")
        return [
            {
                "title": "Fitbod",
                "url": "https://fitbod.me",
                "content": "A popular digital fitness platform offering personalized workouts powered by machine learning, targeting gym-goers."
            },
            {
                "title": "Strava",
                "url": "https://strava.com",
                "content": "A social network for athletes that tracks running and cycling via GPS, popular among college-aged runners."
            },
            {
                "title": "Nike Run Club",
                "url": "https://nike.com",
                "content": "A free running tracker app with guided runs and gamified achievements, heavily used by students."
            }
        ]
        
    # Query LLM to act as a search engine and competitor researcher
    llm = get_llm(temperature=0.2)
    
    prompt = f"""
You are acting as a real-time web search crawler. Find 3 actual competitors or similar products for the following startup idea:
Idea: "{idea}"
Search Query: "{query}"

For each competitor, provide:
1. Title/Name
2. URL (real website URL, e.g. https://example.com)
3. Summary of what they do, their features, and how they target this space.

Return the result STRICTLY as a JSON array of objects with the keys: "title", "url", and "content".
Do not include markdown code block formatting or any explanation text outside the JSON.
"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # Strip markdown ```json block if present
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                content = "\n".join(lines[1:-1])
                
        competitors = json.loads(content)
        return competitors
    except Exception as e:
        logger.error(f"Failed to generate competitor fallback from Gemini: {e}")
        return [
            {
                "title": "Generic Competitor A",
                "url": "https://example.com",
                "content": f"A fitness and wellness service that provides digital solutions related to: {idea}."
            }
        ]

def search_web(query: str, idea: str) -> List[Dict[str, Any]]:
    """
    Search the web for competitors. Uses Tavily if API key is provided, 
    otherwise falls back to LLM-generated search results.
    """
    logger.info(f"Running search for query: '{query}'")
    
    if settings.TAVILY_API_KEY:
        try:
            results = _search_tavily(query)
            logger.info("Successfully fetched search results from Tavily.")
            return results
        except Exception as e:
            logger.error(f"Tavily search failed: {e}. Falling back...")
            
    return _search_fallback_gemini(query, idea)
