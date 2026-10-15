"""
tests/test_degradation.py - Tests for Fault Tolerance and Graceful Degradation (Section 11)
"""

import pytest
from backend.app.graph.runner import execute_analysis_pipeline

@pytest.mark.asyncio
async def test_simulate_feed_down_graceful_handling():
    """
    Simulate pricing feed failure:
    Must not crash, must fall back to cache with stale=True and reduced confidence.
    """
    res = await execute_analysis_pipeline(
        ticker="RELIANCE",
        user_id="meena",
        simulate_feed_down=True
    )

    assert res.session_id is not None
    assert "stale" in res.data_mode
    assert res.recommendation.degraded_flag is True
    # Confirm pipeline completed without uncaught exceptions
    assert res.signals["Momentum Agent"].status == "degraded"
    assert len(res.recommendation.citations) >= 1

@pytest.mark.asyncio
async def test_simulate_missing_filing_wipro():
    """
    Verify WIPRO (which has 0 corporate filings) degrades gracefully:
    Filings agent outputs no_data, recommendation falls back to price/news evidence or wait.
    """
    res = await execute_analysis_pipeline(
        ticker="WIPRO",
        user_id="arjun"
    )

    assert res.signals["Filings RAG Agent"].signal == "no_data"
    assert res.signals["Filings RAG Agent"].status == "degraded"
    assert len(res.signals["Filings RAG Agent"].notes) >= 1
    # Check that recommendation still completed and carries SEBI disclaimer
    assert len(res.disclaimer) > 10

@pytest.mark.asyncio
async def test_tatamotors_agent_conflict_forces_wait():
    """
    Planted scenario for TATAMOTORS:
    Technical momentum is bullish, but earnings call transcript cuts margin guidance (bearish).
    Conflict detector must trigger conflict=True and synthesis must force action='wait'.
    """
    res = await execute_analysis_pipeline(
        ticker="TATAMOTORS",
        user_id="arjun"
    )

    assert res.conflict.conflict is True
    assert res.recommendation.conflict_flag is True
    assert res.recommendation.action == "wait"
    assert res.recommendation.confidence <= 0.50
    assert "Conflict Detected" in res.conflict.explanation

