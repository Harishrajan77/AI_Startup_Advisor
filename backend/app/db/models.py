from sqlalchemy import Column, String, Text, DateTime, JSON
from datetime import datetime
import uuid
from app.db.database import Base

class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    idea = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    current_agent = Column(String, nullable=True)
    
    # Agent Outputs
    plan = Column(Text, nullable=True)
    competitors = Column(JSON, nullable=True)          # List of Dicts
    market_analysis = Column(JSON, nullable=True)      # Dict containing TAM/SAM/SOM
    risks = Column(JSON, nullable=True)                # List of Dicts
    tech_stack = Column(JSON, nullable=True)           # Dict containing stack & MVP scope
    report = Column(Text, nullable=True)               # Final markdown report
    
    # Audit trail
    logs = Column(JSON, nullable=True, default=list)   # List of strings
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "idea": self.idea,
            "status": self.status,
            "current_agent": self.current_agent,
            "plan": self.plan,
            "competitors": self.competitors,
            "market_analysis": self.market_analysis,
            "risks": self.risks,
            "tech_stack": self.tech_stack,
            "report": self.report,
            "logs": self.logs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
