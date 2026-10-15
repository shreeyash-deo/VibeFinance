"""
backend/app/schemas/agent.py - Standard Agent Contracts (Section 6 & 7)
"""

from typing import Literal, Any
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    source_type: Literal['filing', 'news', 'price', 'flow']
    source_id: str # doc_chunk id, url, or 'price:RELIANCE:2026-10-10'
    title: str
    snippet: str # exact text used
    url: str | None = None
    page: int | None = None
    relevance: float | None = None

class AgentOutput(BaseModel):
    agent: str
    ticker: str
    signal: Literal['bullish', 'bearish', 'neutral', 'anomalous', 'no_data']
    confidence: float # 0.0 to 1.0
    reasoning: str # 2-4 sentences, LLM-written from computed facts
    metrics: dict[str, float] # raw computed values (rsi, zscore, etc.)
    evidence: list[Evidence] = []
    latency_ms: int = 0
    status: Literal['ok', 'degraded', 'failed'] = 'ok'
    notes: list[str] = [] # e.g. 'stale data', 'no filings found'

class ConflictReport(BaseModel):
    conflict: bool = False
    pairs: list[tuple[str, str]] = []
    disagreement_score: float = 0.0
    explanation: str = "No critical signal conflict detected."

class RiskVerdict(BaseModel):
    max_position_pct: float = 0.0
    blocked_reasons: list[str] = []
    behavioral_nudges: list[str] = []
    concentration_before: float = 0.0
    concentration_after: float = 0.0
    risk_fit: Literal['good', 'stretch', 'poor'] = 'good'

class Recommendation(BaseModel):
    action: Literal['accumulate', 'hold', 'avoid', 'wait', 'reduce']
    position_size_pct: float
    confidence: float
    summary: str
    citations: list[Evidence] = []
    disclaimer: str = "SEBI Non-Advisory Notice: This intelligence is generated algorithmically for educational and analytical decision support only. It does not constitute investment advice or research analysis under SEBI (Research Analysts) Regulations, 2014."
    concentration_before: float = 0.0
    concentration_after: float = 0.0
    conflict_flag: bool = False
    degraded_flag: bool = False

class TimelineStep(BaseModel):
    step: str
    agent: str
    status: Literal['pending', 'running', 'completed', 'degraded', 'failed']
    latency_ms: int = 0
    detail: str = ""

class FullAnalysisResponse(BaseModel):
    session_id: str
    ticker: str
    user_id: str
    data_mode: str
    as_of: str
    signals: dict[str, AgentOutput]
    conflict: ConflictReport
    risk: RiskVerdict
    recommendation: Recommendation
    timeline: list[TimelineStep]
    session_metrics: dict[str, Any]
    disclaimer: str

