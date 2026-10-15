"""
tests/test_agents.py - Unit & Integration Tests for Specialized Agents
"""

import pytest
import pandas as pd
from backend.app.data import resilient_provider
from backend.app.agents.momentum import run_momentum_agent
from backend.app.agents.volume import run_volume_agent
from backend.app.agents.sentiment import run_sentiment_agent
from backend.app.agents.flow import run_flow_agent
from backend.app.agents.conflict import detect_conflicts

def test_momentum_agent_contract():
    res = resilient_provider.get_prices("INFY", period='1y')
    out = run_momentum_agent("INFY", res.data)
    assert out.agent == "Momentum Agent"
    assert out.ticker == "INFY"
    assert out.signal in ['bullish', 'bearish', 'neutral']
    assert 0.0 <= out.confidence <= 1.0
    assert len(out.reasoning) > 10
    assert len(out.evidence) >= 1
    assert out.status in ['ok', 'degraded']

def test_planted_volume_anomaly_adanient():
    res = resilient_provider.get_prices("ADANIENT", period='1y')
    out = run_volume_agent("ADANIENT", res.data)
    assert out.agent == "Volume Anomaly Agent"
    assert out.ticker == "ADANIENT"
    # Planted volume spike should trigger 'anomalous'
    assert out.signal == "anomalous"
    assert out.metrics["volume_zscore"] >= 2.0
    assert out.confidence >= 0.50

def test_sentiment_agent_contract():
    res = resilient_provider.get_news("INFY", days=14)
    out = run_sentiment_agent("INFY", res.data)
    assert out.agent == "Sentiment Agent"
    assert out.signal in ['bullish', 'bearish', 'neutral']
    assert len(out.evidence) >= 1
    assert out.evidence[0].source_type == "news"

def test_flow_agent_contract():
    res = resilient_provider.get_flows(days=30)
    out = run_flow_agent("RELIANCE", res.data)
    assert out.agent == "Institutional Flow Agent"
    assert out.signal in ['bullish', 'bearish', 'neutral']
    assert "fii_5d_net" in out.metrics
    assert len(out.evidence) >= 1
    assert out.evidence[0].source_type == "flow"

def test_conflict_detection_logic():
    from backend.app.schemas.agent import AgentOutput
    # Simulate conflicting signals
    bullish_out = AgentOutput(
        agent="Momentum Agent",
        ticker="TATAMOTORS",
        signal="bullish",
        confidence=0.80,
        reasoning="Strong technical breakout",
        metrics={},
        evidence=[],
        latency_ms=10,
        status="ok"
    )
    bearish_out = AgentOutput(
        agent="Filings RAG Agent",
        ticker="TATAMOTORS",
        signal="bearish",
        confidence=0.75,
        reasoning="Severe margin guidance cut",
        metrics={},
        evidence=[],
        latency_ms=15,
        status="ok"
    )

    report = detect_conflicts({"Momentum Agent": bullish_out, "Filings RAG Agent": bearish_out})
    assert report.conflict is True
    assert len(report.pairs) >= 1
    assert report.disagreement_score > 0.0
    assert "Conflict Detected" in report.explanation

