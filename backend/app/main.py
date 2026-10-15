"""
backend/app/main.py - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.db.session import init_db
from backend.app.rag.retriever import retriever
from backend.app.api.routes_analysis import router as analysis_router
from backend.app.api.routes_profile import router as profile_router
from backend.app.api.routes_portfolio import router as portfolio_router
from backend.app.api.routes_metrics import router as metrics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables & pre-index filings
    try:
        await init_db()
    except Exception as e:
        print(f"DB init warning: {e}")
    try:
        retriever.load_and_index()
    except Exception as e:
        print(f"Retriever index warning: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Autonomous Financial Intelligence for Retail Investors",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(profile_router, prefix=settings.API_PREFIX)
app.include_router(portfolio_router, prefix=settings.API_PREFIX)
app.include_router(metrics_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "data_mode": settings.DEFAULT_DATA_MODE,
        "default_user_id": settings.DEFAULT_USER_ID,
        "disclaimer": "For educational and decision-support purposes only. Not SEBI registered investment advice."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

