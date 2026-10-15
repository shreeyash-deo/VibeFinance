"""
backend/app/graph/runner.py - Pipeline Execution Harness & SSE Streamer
"""

import uuid
import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from backend.app.graph.build import analysis_graph
from backend.app.data import resilient_provider
from backend.app.schemas.agent import FullAnalysisResponse

DEFAULT_PERSONAS = {
    "meena": {
        "user_id": "meena",
        "display_name": "Meena Iyer",
        "persona_label": "Conservative Retiree",
        "risk_tolerance": "conservative",
        "horizon_years": 3,
        "max_single_stock_pct": 8.0,
        "sector_limits": {"Banking": 40.0, "FMCG": 30.0, "Information Technology": 10.0},
        "loss_aversion": 0.85,
        "overtrading_score": 0.10
    },
    "arjun": {
        "user_id": "arjun",
        "display_name": "Arjun Sharma",
        "persona_label": "Aggressive Momentum Trader",
        "risk_tolerance": "aggressive",
        "horizon_years": 10,
        "max_single_stock_pct": 15.0,
        "sector_limits": {"Information Technology": 45.0, "Automobile": 30.0, "Metals & Mining": 25.0},
        "loss_aversion": 0.30,
        "overtrading_score": 0.40
    },
    "rohan": {
        "user_id": "rohan",
        "display_name": "Rohan Verma",
        "persona_label": "Overtrader / Emotional Investor",
        "risk_tolerance": "moderate",
        "horizon_years": 5,
        "max_single_stock_pct": 10.0,
        "sector_limits": {"Banking": 35.0, "Automobile": 25.0, "FMCG": 20.0},
        "loss_aversion": 0.75,
        "overtrading_score": 0.85
    }
}

DEFAULT_HOLDINGS = {
    "meena": [
        {"ticker": "HDFCBANK", "qty": 150, "avg_price": 1580.0, "sector": "Banking"},
        {"ticker": "ITC", "qty": 400, "avg_price": 440.0, "sector": "FMCG"},
        {"ticker": "TCS", "qty": 20, "avg_price": 3800.0, "sector": "Information Technology"}
    ],
    "arjun": [
        {"ticker": "INFY", "qty": 200, "avg_price": 1720.0, "sector": "Information Technology"},
        {"ticker": "TATAMOTORS", "qty": 350, "avg_price": 920.0, "sector": "Automobile"}
    ],
    "rohan": [
        {"ticker": "SBIN", "qty": 250, "avg_price": 810.0, "sector": "Banking"},
        {"ticker": "ADANIENT", "qty": 40, "avg_price": 3150.0, "sector": "Metals & Mining"}
    ]
}

DEFAULT_BEHAVIOR = {
    "meena": [],
    "arjun": [],
    "rohan": [
        {"action": "sell", "ticker": "ADANIENT", "price": 2890.0, "qty": 20, "tag": "panic_sell", "context": "Sold on 4% gap down"},
        {"action": "sell", "ticker": "TATAMOTORS", "price": 910.0, "qty": 50, "tag": "panic_sell", "context": "Panic sold after broker downgrade"}
    ]
}

async def execute_analysis_pipeline(
    ticker: str,
    user_id: str = "meena",
    data_mode: str = "cached",
    simulate_feed_down: bool = False,
    simulate_missing_filing: bool = False
) -> FullAnalysisResponse:
    """
    Executes end-to-end multi-agent pipeline and returns FullAnalysisResponse.
    """
    session_id = str(uuid.uuid4())
    ticker = ticker.upper()
    user_slug = user_id.lower() if user_id in DEFAULT_PERSONAS else "meena"

    profile = dict(DEFAULT_PERSONAS.get(user_slug, DEFAULT_PERSONAS["meena"]))
    holdings = list(DEFAULT_HOLDINGS.get(user_slug, []))
    behavior = list(DEFAULT_BEHAVIOR.get(user_slug, []))

    # Fetch data inputs via ResilientProvider
    price_res = resilient_provider.get_prices(
        ticker=ticker,
        period='1y',
        data_mode=data_mode,
        simulate_feed_down=simulate_feed_down
    )
    news_res = resilient_provider.get_news(
        ticker=ticker,
        days=14,
        data_mode=data_mode,
        simulate_feed_down=simulate_feed_down
    )
    flows_res = resilient_provider.get_flows(
        days=30,
        data_mode=data_mode,
        simulate_feed_down=simulate_feed_down
    )

    prices_df = price_res.data
    current_prices = {ticker: float(prices_df['Close'].iloc[-1]) if not prices_df.empty else 1000.0}

    initial_state = {
        "session_id": session_id,
        "ticker": ticker,
        "user_id": user_slug,
        "data_mode": data_mode,
        "simulate_feed_down": simulate_feed_down or price_res.stale,
        "simulate_missing_filing": simulate_missing_filing,
        "as_of": price_res.as_of.isoformat(),
        "prices_df": prices_df,
        "news_items": news_res.data if isinstance(news_res.data, list) else [],
        "flows_df": flows_res.data,
        "user_profile": profile,
        "user_holdings": holdings,
        "behavior_events": behavior,
        "current_prices": current_prices,
        "features": {},
        "agent_outputs": {},
        "conflict": None,
        "risk": None,
        "recommendation": None,
        "timeline": [],
        "session_metrics": {},
        "errors": []
    }

    final_state = await analysis_graph.ainvoke(initial_state)

    return FullAnalysisResponse(
        session_id=session_id,
        ticker=ticker,
        user_id=user_slug,
        data_mode="cache (stale)" if initial_state["simulate_feed_down"] else data_mode,
        as_of=initial_state["as_of"],
        signals=final_state["agent_outputs"],
        conflict=final_state["conflict"],
        risk=final_state["risk"],
        recommendation=final_state["recommendation"],
        timeline=final_state["timeline"],
        session_metrics=final_state["session_metrics"],
        disclaimer=final_state["recommendation"].disclaimer
    )

async def stream_analysis_events(
    ticker: str,
    user_id: str = "meena",
    data_mode: str = "cached",
    simulate_feed_down: bool = False,
    simulate_missing_filing: bool = False
) -> AsyncGenerator[str, None]:
    """
    Yields Server-Sent Events (SSE) detailing each pipeline stage live.
    """
    res = await execute_analysis_pipeline(
        ticker=ticker,
        user_id=user_id,
        data_mode=data_mode,
        simulate_feed_down=simulate_feed_down,
        simulate_missing_filing=simulate_missing_filing
    )

    for step in res.timeline:
        event_payload = {
            "type": "timeline_step",
            "step": step.step,
            "agent": step.agent,
            "status": step.status,
            "latency_ms": step.latency_ms,
            "detail": step.detail
        }
        yield f"data: {json.dumps(event_payload)}\n\n"
        await asyncio.sleep(0.04)

    # Final complete analysis payload
    yield f"data: {json.dumps({'type': 'final_result', 'result': res.model_dump()})}\n\n"

