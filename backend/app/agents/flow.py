"""
backend/app/agents/flow.py - Institutional FII/DII Flow Agent
"""

import pandas as pd
from backend.app.schemas.agent import AgentOutput, Evidence
from backend.app.agents.base import safe_run
from backend.app.llm.client import gemini_client

def _run_flow(ticker: str, df_flows: pd.DataFrame, stale: bool = False) -> AgentOutput:
    notes = ["Market-wide institutional liquidity indicator; contextual proxy for domestic equity breadth."]
    evidence = []

    if df_flows.empty:
        return AgentOutput(
            agent="Institutional Flow Agent",
            ticker=ticker,
            signal="neutral",
            confidence=0.40,
            reasoning="Institutional flow telemetry unavailable; defaulting to neutral market context.",
            metrics={"fii_5d_net": 0.0, "dii_5d_net": 0.0, "total_5d_net": 0.0},
            evidence=[],
            latency_ms=0,
            status="degraded",
            notes=["No flow records available."]
        )

    fii_col = "FII_Net_Cr" if "FII_Net_Cr" in df_flows.columns else df_flows.columns[1]
    dii_col = "DII_Net_Cr" if "DII_Net_Cr" in df_flows.columns else df_flows.columns[2]

    fii_5d = float(df_flows[fii_col].iloc[-5:].sum()) if len(df_flows) >= 5 else 0.0
    dii_5d = float(df_flows[dii_col].iloc[-5:].sum()) if len(df_flows) >= 5 else 0.0
    total_5d = fii_5d + dii_5d

    fii_20d = float(df_flows[fii_col].iloc[-20:].sum()) if len(df_flows) >= 20 else 0.0
    dii_20d = float(df_flows[dii_col].iloc[-20:].sum()) if len(df_flows) >= 20 else 0.0
    total_20d = fii_20d + dii_20d

    last_date = str(df_flows['Date'].iloc[-1]) if 'Date' in df_flows.columns else "Recent"

    if total_5d > 1500.0:
        signal = "bullish"
        conf = 0.65
    elif total_5d < -1500.0:
        signal = "bearish"
        conf = 0.65
    else:
        signal = "neutral"
        conf = 0.50

    if stale:
        conf = max(0.20, conf - 0.15)
        notes.append("Flows sourced from cached snapshot dataset.")

    evidence.append(Evidence(
        source_type="flow",
        source_id=f"flow:NSE:{last_date}",
        title="NSE Institutional Provisional Flow Snapshot",
        snippet=f"5-day cumulative net flows: FII Rs {fii_5d:,.1f} Cr, DII Rs {dii_5d:,.1f} Cr (Total net: Rs {total_5d:,.1f} Cr as of {last_date}).",
        url=None,
        relevance=0.80
    ))

    prompt = (
        f"You are the Institutional Flow Agent. Summarize 5-day market liquidity in 2 sentences: "
        f"FII 5d: Rs {fii_5d:.1f} Cr, DII 5d: Rs {dii_5d:.1f} Cr, Total: Rs {total_5d:.1f} Cr ({signal}). Factual only."
    )
    reasoning = gemini_client.generate(prompt)
    if not reasoning or "Deterministic" in reasoning or len(reasoning) < 20:
        stance = "positive net liquidity expansion" if signal == "bullish" else ("net capital distribution" if signal == "bearish" else "balanced cross-currents")
        reasoning = (
            f"Over the last 5 trading sessions, institutional flows registered {stance} with DIIs absorbing "
            f"Rs {dii_5d:,.1f} Cr against FII net flows of Rs {fii_5d:,.1f} Cr, providing supportive domestic liquidity breadth."
        )

    return AgentOutput(
        agent="Institutional Flow Agent",
        ticker=ticker,
        signal=signal,
        confidence=round(conf, 2),
        reasoning=reasoning.strip(),
        metrics={
            "fii_5d_net": round(fii_5d, 2),
            "dii_5d_net": round(dii_5d, 2),
            "total_5d_net": round(total_5d, 2),
            "fii_20d_net": round(fii_20d, 2),
            "dii_20d_net": round(dii_20d, 2),
            "total_20d_net": round(total_20d, 2)
        },
        evidence=evidence,
        latency_ms=0,
        status="ok" if not stale else "degraded",
        notes=notes
    )

def run_flow_agent(ticker: str, df_flows: pd.DataFrame, stale: bool = False) -> AgentOutput:
    return safe_run("Institutional Flow Agent", ticker, _run_flow, ticker, df_flows, stale)

