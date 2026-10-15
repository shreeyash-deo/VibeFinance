"""
backend/app/graph/build.py - LangGraph Multi-Agent Orchestration Graph
"""

import time
import asyncio
from typing import Any
from langgraph.graph import StateGraph, START, END

from backend.app.graph.state import GraphState
from backend.app.schemas.agent import TimelineStep
from backend.app.features.indicators import compute_technical_features
from backend.app.agents.momentum import run_momentum_agent
from backend.app.agents.volume import run_volume_agent
from backend.app.agents.sentiment import run_sentiment_agent
from backend.app.agents.filings_rag import run_filings_rag_agent
from backend.app.agents.flow import run_flow_agent
from backend.app.agents.conflict import detect_conflicts
from backend.app.agents.risk import evaluate_investor_risk
from backend.app.agents.synthesis import synthesize_recommendation

async def ingest_node(state: GraphState) -> dict[str, Any]:
    t0 = time.perf_counter()
    timeline = list(state.get("timeline", []))
    timeline.append(TimelineStep(
        step="Data Ingestion",
        agent="ResilientProvider",
        status="completed",
        latency_ms=int((time.perf_counter() - t0) * 1000),
        detail=f"Ingested OHLCV, news, flows, and filings for {state['ticker']} (Mode: {state['data_mode']})"
    ))
    return {"timeline": timeline}

async def features_node(state: GraphState) -> dict[str, Any]:
    t0 = time.perf_counter()
    df = state.get("prices_df")
    features = compute_technical_features(df)
    lat = int((time.perf_counter() - t0) * 1000)
    timeline = list(state.get("timeline", []))
    timeline.append(TimelineStep(
        step="Feature Engineering",
        agent="Deterministic Engine",
        status="completed",
        latency_ms=lat,
        detail=f"Computed RSI ({features['rsi']}), MACD, SMAs, and Volume Z-Score ({features['volume_zscore']})"
    ))
    return {"features": features, "timeline": timeline}

async def parallel_agents_node(state: GraphState) -> dict[str, Any]:
    """
    Executes 5 specialized agents concurrently in parallel using asyncio.to_thread / gather.
    """
    ticker = state["ticker"]
    prices_df = state["prices_df"]
    news = state.get("news_items", [])
    flows_df = state.get("flows_df")
    stale = state.get("simulate_feed_down", False)
    missing_filings = state.get("simulate_missing_filing", False)

    # Launch parallel agent tasks
    t_start = time.perf_counter()
    tasks = [
        asyncio.to_thread(run_momentum_agent, ticker, prices_df, stale),
        asyncio.to_thread(run_volume_agent, ticker, prices_df, stale),
        asyncio.to_thread(run_sentiment_agent, ticker, news, stale),
        asyncio.to_thread(run_filings_rag_agent, ticker, missing_filings),
        asyncio.to_thread(run_flow_agent, ticker, flows_df, stale)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    parallel_lat = int((time.perf_counter() - t_start) * 1000)

    agent_outputs = {}
    timeline = list(state.get("timeline", []))

    agent_names = [
        "Momentum Agent",
        "Volume Anomaly Agent",
        "Sentiment Agent",
        "Filings RAG Agent",
        "Institutional Flow Agent"
    ]

    for name, res in zip(agent_names, results):
        if isinstance(res, Exception):
            from backend.app.schemas.agent import AgentOutput
            res = AgentOutput(
                agent=name,
                ticker=ticker,
                signal="no_data",
                confidence=0.0,
                reasoning=f"Agent crashed: {str(res)}",
                metrics={},
                evidence=[],
                latency_ms=parallel_lat,
                status="failed",
                notes=[str(res)]
            )
        agent_outputs[name] = res
        timeline.append(TimelineStep(
            step="Signal Classification",
            agent=name,
            status="completed" if res.status == "ok" else ("degraded" if res.status == "degraded" else "failed"),
            latency_ms=res.latency_ms,
            detail=f"Signal: {res.signal.upper()} (Confidence: {int(res.confidence * 100)}%)"
        ))

    return {"agent_outputs": agent_outputs, "timeline": timeline}

async def conflict_node(state: GraphState) -> dict[str, Any]:
    t0 = time.perf_counter()
    conflict_report = detect_conflicts(state["agent_outputs"])
    lat = int((time.perf_counter() - t0) * 1000)

    timeline = list(state.get("timeline", []))
    timeline.append(TimelineStep(
        step="Conflict Detection",
        agent="Conflict Detector",
        status="completed",
        latency_ms=lat,
        detail=f"Conflict: {'YES' if conflict_report.conflict else 'NO'} (Disagreement: {conflict_report.disagreement_score})"
    ))
    return {"conflict": conflict_report, "timeline": timeline}

async def risk_node(state: GraphState) -> dict[str, Any]:
    t0 = time.perf_counter()
    features = state.get("features", {})
    vol = float(features.get("volatility_60d", 20.0))
    filings_out = state["agent_outputs"].get("Filings RAG Agent")

    risk_verdict = evaluate_investor_risk(
        ticker=state["ticker"],
        sector=state["user_profile"].get("sector", "Diversified"),
        profile=state["user_profile"],
        holdings=state.get("user_holdings", []),
        current_prices=state.get("current_prices", {}),
        volatility_60d=vol,
        behavior_events=state.get("behavior_events", []),
        filings_agent_output=filings_out
    )
    lat = int((time.perf_counter() - t0) * 1000)

    timeline = list(state.get("timeline", []))
    timeline.append(TimelineStep(
        step="Risk & Behavioral Profiling",
        agent="Risk Agent",
        status="completed",
        latency_ms=lat,
        detail=f"Fit: {risk_verdict.risk_fit.upper()}, Max Position: {risk_verdict.max_position_pct}%"
    ))
    return {"risk": risk_verdict, "timeline": timeline}

async def synthesis_node(state: GraphState) -> dict[str, Any]:
    t0 = time.perf_counter()
    rec = synthesize_recommendation(
        ticker=state["ticker"],
        agent_outputs=state["agent_outputs"],
        conflict=state["conflict"],
        risk=state["risk"],
        profile=state["user_profile"]
    )
    lat = int((time.perf_counter() - t0) * 1000)

    timeline = list(state.get("timeline", []))
    timeline.append(TimelineStep(
        step="Intelligence Synthesis",
        agent="Synthesis Agent",
        status="completed",
        latency_ms=lat,
        detail=f"Action: {rec.action.upper()} | Position: {rec.position_size_pct}% | Confidence: {int(rec.confidence * 100)}%"
    ))
    return {"recommendation": rec, "timeline": timeline}

async def evaluation_node(state: GraphState) -> dict[str, Any]:
    """
    Computes required session performance metrics (Section 12 of spec).
    """
    outputs = state.get("agent_outputs", {})
    agent_latencies = {f"latency_{name.lower().replace(' ', '_')}_ms": out.latency_ms for name, out in outputs.items()}
    sequential_est = sum(out.latency_ms for out in outputs.values())

    rec = state.get("recommendation")
    filings_out = outputs.get("Filings RAG Agent")
    retrieval_relevance = filings_out.metrics.get("retrieval_relevance", 1.0) if filings_out else 0.0

    ok_count = sum(1 for out in outputs.values() if out.status == "ok")

    timeline = state.get("timeline", [])
    total_pipeline_ms = sum(t.latency_ms for t in timeline)

    session_metrics = {
        **agent_latencies,
        "latency_total_ms": total_pipeline_ms,
        "latency_sequential_est_ms": sequential_est,
        "concentration_before": rec.concentration_before if rec else 0.0,
        "concentration_after": rec.concentration_after if rec else 0.0,
        "retrieval_relevance": retrieval_relevance,
        "agents_ok_count": ok_count,
        "degraded_flag": bool(rec.degraded_flag if rec else False)
    }

    return {"session_metrics": session_metrics}

def build_analysis_graph():
    """Builds and compiles the LangGraph multi-agent DAG."""
    builder = StateGraph(GraphState)

    builder.add_node("ingest", ingest_node)
    builder.add_node("features", features_node)
    builder.add_node("parallel_agents", parallel_agents_node)
    builder.add_node("conflict", conflict_node)
    builder.add_node("risk", risk_node)
    builder.add_node("synthesis", synthesis_node)
    builder.add_node("evaluation", evaluation_node)

    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "features")
    builder.add_edge("features", "parallel_agents")
    builder.add_edge("parallel_agents", "conflict")
    builder.add_edge("conflict", "risk")
    builder.add_edge("risk", "synthesis")
    builder.add_edge("synthesis", "evaluation")
    builder.add_edge("evaluation", END)

    return builder.compile()

analysis_graph = build_analysis_graph()

