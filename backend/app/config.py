import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App General Settings
    PROJECT_NAME: str = Field(default="AI Startup Advisor", description="Name of the project")

    # API Keys
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    TAVILY_API_KEY: str = Field(default="", description="Tavily Web Search API Key (Optional)")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", description="Google Gemini Model Name")
    
    # Groq Configuration
    MODEL_PROVIDER: str = Field(default="gemini", description="LLM Provider: gemini or groq")
    GROQ_API_KEY: str = Field(default="", description="Groq API Key")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Groq Model Name")
    
    # Database Configuration
    # Default to a local SQLite database in the backend directory
    DATABASE_URL: str = Field(
        default="sqlite:///./startup_advisor.db",
        description="SQLAlchemy database URL. Fallback is local SQLite."
    )
    
    # RAG Configuration
    KNOWLEDGE_BASE_DIR: str = Field(
        default="./knowledge_base",
        description="Path to knowledge base markdown files"
    )
    VECTOR_STORE_DIR: str = Field(
        default="./faiss_index",
        description="Directory to save the built FAISS index"
    )
    
    # App Settings
    PORT: int = Field(default=8000, description="Backend API Port")
    HOST: str = Field(default="0.0.0.0", description="Backend Host")

    # Load from .env file at backend/
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings singleton
settings = Settings()

# Centralized LLM factories
def has_llm_credentials() -> bool:
    """Checks if active model provider credentials are provided."""
    if settings.MODEL_PROVIDER.lower() == "groq":
        return bool(settings.GROQ_API_KEY.strip())
    return bool(settings.GEMINI_API_KEY.strip())

def get_llm(temperature: float = 0.2):
    """Instantiate the centralized LLM model based on settings."""
    if settings.MODEL_PROVIDER.lower() == "groq":
        from langchain_groq import ChatGroq
        if not settings.GROQ_API_KEY.strip():
            raise ValueError("GROQ_API_KEY is missing but MODEL_PROVIDER is set to groq.")
        return ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature
        )
    else:
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not settings.GEMINI_API_KEY.strip():
            raise ValueError("GEMINI_API_KEY is missing but MODEL_PROVIDER is set to gemini.")
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature
        )
