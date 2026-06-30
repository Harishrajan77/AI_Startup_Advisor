import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db, SessionLocal
from app.db.models import ValidationRun
from app.agents.workflow import agent_graph
from pydantic import BaseModel

logger = logging.getLogger("startup_advisor.routes")
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api")

# Pydantic models for validation
class ValidationRequest(BaseModel):
    idea: str

class ValidationSummary(BaseModel):
    id: str
    idea: str
    status: str
    created_at: str

    class Config:
        from_attributes = True

async def execute_agent_workflow(run_id: str, idea: str):
    """
    Executes the compiled LangGraph workflow in the background and 
    saves intermediate outputs to the SQL database.
    """
    logger.info(f"Starting background workflow execution for run {run_id}")
    
    # Create a new database session for this background task
    db = SessionLocal()
    
    try:
        # Update run status to RUNNING
        run = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
        if not run:
            logger.error(f"Validation run {run_id} not found in DB.")
            return
            
        run.status = "RUNNING"
        run.current_agent = "planner"
        run.logs = ["Workflow started. Initiating Planner Agent..."]
        db.commit()
        
        # Initial input state
        initial_state = {
            "idea": idea,
            "plan": "",
            "competitors": [],
            "market_analysis": {},
            "risks": {},
            "tech_stack": {},
            "report": "",
            "logs": run.logs,
            "current_agent": "planner"
        }
        
        # Stream the graph execution asynchronously node-by-node
        async for event in agent_graph.astream(initial_state):
            # event is a dict of {node_name: state_updates}
            node_name = list(event.keys())[0]
            updates = event[node_name]
            
            # Fetch the model again to prevent session detachment issues
            run = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
            if not run:
                break
                
            # Update specific output fields and logs based on which agent completed
            if "plan" in updates and updates["plan"]:
                run.plan = updates["plan"]
            if "competitors" in updates and updates["competitors"]:
                run.competitors = updates["competitors"]
            if "market_analysis" in updates and updates["market_analysis"]:
                run.market_analysis = updates["market_analysis"]
            if "risks" in updates and updates["risks"]:
                run.risks = updates["risks"]
            if "tech_stack" in updates and updates["tech_stack"]:
                run.tech_stack = updates["tech_stack"]
            if "report" in updates and updates["report"]:
                run.report = updates["report"]
                
            if "current_agent" in updates:
                run.current_agent = updates["current_agent"]
            if "logs" in updates:
                # Merge and preserve order
                run.logs = updates["logs"]
                
            db.commit()
            logger.info(f"Node '{node_name}' completed. DB updated for run {run_id}")
            
            # Short sleep to prevent racing and mimic real-time visual progress
            await asyncio.sleep(0.5)
            
        # Final completed updates
        run = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
        if run:
            run.status = "COMPLETED"
            run.current_agent = "done"
            # Append final success log if not already there
            current_logs = list(run.logs or [])
            if "Workflow complete." not in current_logs:
                current_logs.append("Workflow complete. Validation report generated successfully.")
            run.logs = current_logs
            db.commit()
            logger.info(f"Workflow execution completed for run {run_id}")
            
    except Exception as e:
        logger.error(f"Error executing agent workflow for run {run_id}: {e}", exc_info=True)
        # Re-fetch and mark as FAILED
        try:
            run = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
            if run:
                run.status = "FAILED"
                current_logs = list(run.logs or [])
                current_logs.append(f"CRITICAL ERROR: Execution halted. Reason: {e}")
                run.logs = current_logs
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to record execution error to DB: {db_err}")
    finally:
        db.close()

@router.post("/validate")
def validate_startup_idea(request: ValidationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Submits a startup idea and kicks off the multi-agent LangGraph workflow."""
    if not request.idea.strip():
        raise HTTPException(status_code=400, detail="Startup idea description cannot be empty.")
        
    try:
        # Create validation record
        new_run = ValidationRun(
            idea=request.idea,
            status="PENDING",
            logs=["Initializing advisor context database record..."]
        )
        db.add(new_run)
        db.commit()
        db.refresh(new_run)
        
        # Enqueue the background task
        background_tasks.add_task(execute_agent_workflow, new_run.id, new_run.idea)
        
        return new_run.to_dict()
    except Exception as e:
        logger.error(f"Failed to submit validation request: {e}")
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {e}")

@router.get("/validate/{run_id}")
def get_validation_status(run_id: str, db: Session = Depends(get_db)):
    """Retrieves current execution status, log messages, and results for a run."""
    run = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Validation run not found.")
    return run.to_dict()

@router.get("/history")
def get_validation_history(db: Session = Depends(get_db)):
    """Fetches a list of previous validation runs sorted by creation time."""
    runs = db.query(ValidationRun).order_by(ValidationRun.created_at.desc()).all()
    return [
        {
            "id": run.id,
            "idea": run.idea,
            "status": run.status,
            "created_at": run.created_at.isoformat() if run.created_at else None
        }
        for run in runs
    ]
