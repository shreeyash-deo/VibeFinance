"""
tests/test_rag.py - Tests for Corrective RAG (CRAG) and Citation Grounding
"""

import pytest
from backend.app.rag.retriever import retriever
from backend.app.agents.filings_rag import run_filings_rag_agent

def test_adanient_promoter_pledge_retrieval():
    out = run_filings_rag_agent("ADANIENT")
    assert out.agent == "Filings RAG Agent"
    assert out.status == "ok"
    assert out.signal == "bearish" # Planted pledge hike 12%->19% should classify bearish
    assert len(out.evidence) >= 1

    # Verify that evidence contains promoter pledge or auditor note
    has_pledge_or_audit = any("pledge" in ev.snippet.lower() or "encumbrance" in ev.snippet.lower() or "auditor" in ev.snippet.lower() for ev in out.evidence)
    assert has_pledge_or_audit is True

    # Validate that every cited chunk ID exists in the retriever database
    for ev in out.evidence:
        assert ev.source_type == "filing"
        chunk_obj = retriever.get_chunk_by_id(ev.source_id)
        assert chunk_obj is not None
        assert chunk_obj["ticker"] == "ADANIENT"

def test_wipro_missing_filing_graceful_degradation():
    out = run_filings_rag_agent("WIPRO")
    assert out.agent == "Filings RAG Agent"
    assert out.ticker == "WIPRO"
    assert out.signal == "no_data"
    assert out.status == "degraded"
    assert out.confidence == 0.0
    assert any("No supporting" in n for n in out.notes)
    # Pipeline did not raise any exception!

