"""
tests/test_personalization.py - Tests for Personalized Risk Profiling and Behavioral Nudges
"""

import pytest
import asyncio
from backend.app.graph.runner import execute_analysis_pipeline

@pytest.mark.asyncio
async def test_adanient_differentiation_across_three_personas():
    """
    Assert that the same stock (ADANIENT) produces differentiated outputs
    across Meena, Arjun, and Rohan.
    """
    meena_res = await execute_analysis_pipeline(ticker="ADANIENT", user_id="meena")
    arjun_res = await execute_analysis_pipeline(ticker="ADANIENT", user_id="arjun")
    rohan_res = await execute_analysis_pipeline(ticker="ADANIENT", user_id="rohan")

    # 1. Meena (Conservative Retiree) should reject allocation (0% cap) due to high volatility / pledge risk
    assert meena_res.risk.risk_fit in ["poor", "stretch"]
    assert meena_res.recommendation.position_size_pct == 0.0
    assert meena_res.recommendation.action in ["avoid", "wait"]

    # 2. Arjun (Aggressive Trader) has higher risk ceiling and accommodates volatile equities
    assert arjun_res.risk.max_position_pct >= meena_res.risk.max_position_pct

    # 3. Rohan (Overtrader with past panic sells) must receive a 48-hour cooling-off behavioral nudge
    has_cooling_off = any("48-hour cooling-off" in n for n in rohan_res.risk.behavioral_nudges)
    assert has_cooling_off is True
    assert rohan_res.recommendation.action == "wait"
    assert rohan_res.recommendation.position_size_pct == 0.0

@pytest.mark.asyncio
async def test_infy_differentiation_across_three_personas():
    """
    Assert that INFY produces distinct position caps based on sector limits and risk tolerance.
    """
    meena_res = await execute_analysis_pipeline(ticker="INFY", user_id="meena")
    arjun_res = await execute_analysis_pipeline(ticker="INFY", user_id="arjun")

    # Arjun has an aggressive IT allocation ceiling (45% sector, 15% single stock)
    # Meena has an IT limit capped at 10%
    assert arjun_res.risk.max_position_pct > meena_res.risk.max_position_pct

