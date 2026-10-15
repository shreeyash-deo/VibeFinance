"""
backend/app/graph/state.py - LangGraph Execution State Definition
"""

from typing import TypedDict, Any
from backend.app.schemas.agent import AgentOutput, ConflictReport, RiskVerdict, Recommendation, TimelineStep

class GraphState(TypedDict):
    session_id: str
    ticker: str
    user_id: str
    data_mode: str
    simulate_feed_down: bool
    simulate_missing_filing: bool
    as_of: str
    prices_df: Any
    news_items: list[dict]
    flows_df: Any
    user_profile: dict[str, Any]
    user_holdings: list[dict[str, Any]]
    behavior_events: list[dict[str, Any]]
    current_prices: dict[str, float]
    features: dict[str, Any]
    agent_outputs: dict[str, AgentOutput]
    conflict: ConflictReport
    risk: RiskVerdict
    recommendation: Recommendation
    timeline: list[TimelineStep]
    session_metrics: dict[str, Any]
    errors: list[str]

