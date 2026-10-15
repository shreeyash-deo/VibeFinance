"""
backend/app/config.py - Application Configuration
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "VibeFinance"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Environment & Host
    DEBUG: bool = True
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    # Defaults to local async sqlite, can be overridden by DATABASE_URL (e.g. postgresql+asyncpg://...)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite+aiosqlite:///{BACKEND_DIR / 'vibefinance.db'}"
    )
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # Embeddings
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    
    # Data Mode
    DEFAULT_DATA_MODE: str = os.getenv("DEFAULT_DATA_MODE", "cached")
    DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "meena")
    
    # Global Simulation Flags
    SIMULATE_FEED_DOWN: bool = False
    SIMULATE_MISSING_FILING: bool = False
    
    # Data Paths
    SNAPSHOT_DIR: Path = ROOT_DIR / "data_snapshot"
    PRICES_DIR: Path = SNAPSHOT_DIR / "prices"
    NEWS_DIR: Path = SNAPSHOT_DIR / "news"
    FILINGS_DIR: Path = SNAPSHOT_DIR / "filings"
    FLOWS_FILE: Path = SNAPSHOT_DIR / "flows.csv"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Fallback path checking
if not settings.SNAPSHOT_DIR.exists() and (BACKEND_DIR / "data_snapshot").exists():
    settings.SNAPSHOT_DIR = BACKEND_DIR / "data_snapshot"
    settings.PRICES_DIR = settings.SNAPSHOT_DIR / "prices"
    settings.NEWS_DIR = settings.SNAPSHOT_DIR / "news"
    settings.FILINGS_DIR = settings.SNAPSHOT_DIR / "filings"
    settings.FLOWS_FILE = settings.SNAPSHOT_DIR / "flows.csv"

