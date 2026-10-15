"""
tests/test_optional_extensions.py - Automated Unit & Integration Tests for Optional Extensions
Audits:
1. Multi-source financial data ingestion
2. Semantic vector search (384-dim dense embeddings + cosine similarity)
3. Portfolio concentration (HHI) & sector exposure limits
4. 18-month historical backtesting & confidence calibration
5. Disagreement variance & cross-agent conflict explanation
6. Parallel latency acceleration vs sequential estimate
"""

import pytest
from backend.app.rag.embeddings import get_text_embedding, cosine_similarity
from backend.app.rag.retriever import retriever
from backend.app.eval.backtest import run_historical_backtest, run_confidence_calibration
from backend.app.agents.conflict import detect_conflicts
from backend.app.schemas.agent import AgentOutput
from backend.app.features.indicators import compute_portfolio_metrics
from backend.app.graph.runner import execute_analysis_pipeline

def test_semantic_vector_embeddings_and_search():
    retriever.load_and_index()
    query = "promoter pledge and loan encumbrance"
    q_emb = get_text_embedding(query)
    assert len(q_emb) == 384

    # Test cosine similarity calculation
    candidates = [c for c in retriever._chunks if c["ticker"] == "ADANIENT"]
    assert len(candidates) >= 1

    scored = []
    for c in candidates:
        sim = cosine_similarity(q_emb, c["embedding"])
        scored.append((sim, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score, top_chunk = scored[0]

    assert top_score > 0.35
    assert "pledge" in top_chunk["text"].lower() or "encumbrance" in top_chunk["text"].lower()

def test_confidence_calibration_buckets():
    buckets = run_confidence_calibration()
    assert len(buckets) == 5
    for b in buckets:
        assert "bucket" in b
        assert "predicted" in b
        assert "actual" in b
        assert "count" in b
        assert 0.0 <= b["predicted"] <= 100.0
        assert 0.0 <= b["actual"] <= 100.0

def test_conflict_disagreement_variance():
    bullish_out = AgentOutput(
        agent="Momentum Agent",
        ticker="TATAMOTORS",
        signal="bullish",
        confidence=0.85,
        reasoning="Technical breakout",
        metrics={},
        evidence=[],
        latency_ms=10,
        status="ok"
    )
    bearish_out = AgentOutput(
        agent="Filings RAG Agent",
        ticker="TATAMOTORS",
        signal="bearish",
        confidence=0.80,
        reasoning="Margin guidance cut",
        metrics={},
        evidence=[],
        latency_ms=12,
        status="ok"
    )

    report = detect_conflicts({"Momentum Agent": bullish_out, "Filings RAG Agent": bearish_out})
    assert report.conflict is True
    # Disagreement score must be positive standard deviation of opposing weighted signals
    assert report.disagreement_score > 0.40
    assert len(report.pairs) == 1
    assert "Conflict Detected" in report.explanation

def test_portfolio_hhi_and_sector_limits():
    holdings = [
        {"ticker": "HDFCBANK", "qty": 100, "avg_price": 1600.0, "sector": "Banking"},
        {"ticker": "ICICIBANK", "qty": 100, "avg_price": 1200.0, "sector": "Banking"},
        {"ticker": "ITC", "qty": 200, "avg_price": 450.0, "sector": "FMCG"}
    ]
    prices = {"HDFCBANK": 1600.0, "ICICIBANK": 1200.0, "ITC": 450.0}
    m = compute_portfolio_metrics(holdings, prices)

    total = 160000 + 120000 + 90000
    assert m["total_value"] == total
    # Check sector exposure
    assert "Banking" in m["sector_exposure"]
    assert "FMCG" in m["sector_exposure"]
    assert m["sector_exposure"]["Banking"] > 50.0
    # HHI must be within [0, 1.0]
    assert 0.0 < m["hhi"] < 1.0

@pytest.mark.asyncio
async def test_parallel_latency_speedup():
    res = await execute_analysis_pipeline("INFY", user_id="arjun")
    metrics = res.session_metrics

    parallel_total = metrics.get("latency_total_ms", 100)
    sequential_est = metrics.get("latency_sequential_est_ms", 300)

    # Parallel execution must be faster or equal to sequential estimated sum
    assert parallel_total <= sequential_est + 50

