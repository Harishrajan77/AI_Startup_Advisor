import logging
import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from app.config import settings, has_llm_credentials, get_llm
from app.tools.search import search_web

logger = logging.getLogger("startup_advisor.agents.researcher")

def run_researcher(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Competitor Research Agent: Performs web searches to identify and analyze 
    direct and indirect competitors.
    """
    idea = state["idea"]
    logger.info(f"Running Competitor Research Agent for idea: '{idea[:50]}'")
    
    logs = list(state.get("logs") or [])
    logs.append("Competitor Research Agent: Searching web for existing competitors...")
    
    # 1. Execute Search
    search_query = f"{idea} competitors products apps"
    search_results = search_web(search_query, idea)
    
    logs.append(f"Competitor Research Agent: Analyzing search hits...")
    
    if not has_llm_credentials():
        # Fallback competitor list
        mock_competitors = [
            {
                "name": "Fitbod",
                "url": "https://fitbod.me",
                "description": "Uses machine learning to build personalized workout routines based on gym equipment availability.",
                "strengths": "Great algorithm, supports complex gym environments.",
                "weaknesses": "Subscription is expensive for students; lacks campus social integration."
            },
            {
                "name": "Strava",
                "url": "https://strava.com",
                "description": "Leading social network for athletes to track outdoor running, cycling, and walking.",
                "strengths": "Extremely strong community features, viral network effects.",
                "weaknesses": "Focuses heavily on endurance sports, not generic gym/dorm workouts."
            },
            {
                "name": "Freeletics",
                "url": "https://freeletics.com",
                "description": "Bodyweight fitness app featuring AI coach, focusing on high-intensity workouts with no equipment.",
                "strengths": "Excellent for small spaces like dorm rooms.",
                "weaknesses": "Lacks real-time multiplayer workout tracking or college community ties."
            }
        ]
        return {
            "competitors": mock_competitors,
            "current_agent": "researcher",
            "logs": logs + ["Competitor Research Agent: Extracted 3 competitors (Mock Fallback)."]
        }
        
    try:
        llm = get_llm(temperature=0.2)
        
        results_str = json.dumps(search_results, indent=2)
        prompt = f"""
You are a competitive intelligence analyst (Competitor Research Agent).
Analyze these search results and extract the top 3-4 competitors for this startup idea:
Idea: "{idea}"

Search results:
{results_str}

For each competitor, synthesize:
1. Name
2. Website URL (must match the search result URL, or use a placeholder)
3. Concise description of their value proposition
4. Strengths (what they do well)
5. Weaknesses (what they miss, or how they fail to address our target audience)

Return the result STRICTLY as a JSON array of objects with the keys: "name", "url", "description", "strengths", "weaknesses".
Do not include markdown formatting or explanation text.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                content = "\n".join(lines[1:-1])
                
        competitors = json.loads(content)
        
        return {
            "competitors": competitors,
            "current_agent": "researcher",
            "logs": logs + [f"Competitor Research Agent: Extracted and structured {len(competitors)} competitors."]
        }
    except Exception as e:
        logger.error(f"Error in Competitor Research Agent: {e}")
        mock_competitors = [
            {
                "name": "Fitbod",
                "url": "https://fitbod.me",
                "description": "Uses machine learning to build personalized workout routines based on gym equipment availability.",
                "strengths": "Great algorithm, supports complex gym environments.",
                "weaknesses": "Subscription is expensive for students; lacks campus social integration."
            },
            {
                "name": "Strava",
                "url": "https://strava.com",
                "description": "Leading social network for athletes to track outdoor running, cycling, and walking.",
                "strengths": "Extremely strong community features, viral network effects.",
                "weaknesses": "Focuses heavily on endurance sports, not generic gym/dorm workouts."
            },
            {
                "name": "Freeletics",
                "url": "https://freeletics.com",
                "description": "Bodyweight fitness app featuring AI coach, focusing on high-intensity workouts with no equipment.",
                "strengths": "Excellent for small spaces like dorm rooms.",
                "weaknesses": "Lacks real-time multiplayer workout tracking or college community ties."
            }
        ]
        return {
            "competitors": mock_competitors,
            "current_agent": "researcher",
            "logs": logs + [f"Competitor Research Agent: Extracted 3 competitors (parametric fallback: {e})."]
        }
