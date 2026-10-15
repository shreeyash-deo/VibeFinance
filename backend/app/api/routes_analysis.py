"""
backend/app/api/routes_analysis.py - Analysis & Streaming Endpoints
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from backend.app.schemas.api import AnalyzeRequest
from backend.app.schemas.agent import FullAnalysisResponse
from backend.app.graph.runner import execute_analysis_pipeline, stream_analysis_events
from backend.app.deps import get_current_user_id

router = APIRouter(tags=["Analysis"])

@router.post("/analyze", response_model=FullAnalysisResponse)
async def analyze_stock(
    req: AnalyzeRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Executes the multi-agent autonomous analysis pipeline for a specified ticker and investor persona.
    """
    user_id = req.user_id if req.user_id else current_user_id
    response = await execute_analysis_pipeline(
        ticker=req.ticker,
        user_id=user_id,
        data_mode=req.data_mode,
        simulate_feed_down=req.simulate_feed_down,
        simulate_missing_filing=req.simulate_missing_filing
    )
    return response

@router.get("/analyze/stream/{ticker}")
async def stream_analysis(
    ticker: str,
    user_id: str = Query("meena"),
    data_mode: str = Query("cached"),
    simulate_feed_down: bool = Query(False),
    simulate_missing_filing: bool = Query(False)
):
    """
    Streams Server-Sent Events (SSE) detailing agent execution progress live to the frontend.
    """
    generator = stream_analysis_events(
        ticker=ticker,
        user_id=user_id,
        data_mode=data_mode,
        simulate_feed_down=simulate_feed_down,
        simulate_missing_filing=simulate_missing_filing
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

