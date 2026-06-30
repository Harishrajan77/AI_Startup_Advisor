from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings

# If using SQLite, we need some additional connect arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Create the database engine
# If using SQLite in-memory or file, we can optionally use StaticPool if in-memory, 
# but for a standard file sqlite database, standard configuration is fine.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for models
Base = declarative_base()

def get_db():
    """FastAPI database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
