"""
backend/app/agents/volume.py - Deterministic Volume Anomaly Agent
"""

import pandas as pd
from backend.app.schemas.agent import AgentOutput, Evidence
from backend.app.features.indicators import compute_technical_features
from backend.app.agents.base import safe_run
from backend.app.llm.client import gemini_client

def _run_volume(ticker: str, df: pd.DataFrame, stale: bool = False) -> AgentOutput:
    metrics = compute_technical_features(df)
    notes = ["Delivery percentage not available in current exchange feed (provisional estimate)."]
    evidence = []

    z_score = metrics["volume_zscore"]
    vol_ratio = metrics["volume_ratio_20d"]
    latest_close = metrics["latest_close"]
    latest_volume = metrics["latest_volume"]

    price_change_1d = 0.0
    if len(df) >= 2:
        prev_close = float(df['Close'].iloc[-2])
        price_change_1d = round(((latest_close - prev_close) / prev_close) * 100, 2)

    metrics["price_change_1d"] = price_change_1d

    last_date_str = str(df['Date'].iloc[-1].strftime("%Y-%m-%d")) if not df.empty else "Recent"

    # Volume anomaly evaluation
    if z_score >= 2.0:
        signal = "anomalous"
        bias = "bullish" if price_change_1d >= 0 else "bearish"
        metrics["anomaly_bias"] = 1.0 if bias == "bullish" else -1.0
        conf = 0.40 + (min(z_score / 4.0, 1.0) * (0.85 - 0.40))
        notes.append(f"Significant institutional volume anomaly detected ({vol_ratio}x 20-day average, z-score {z_score}).")
    else:
        signal = "neutral"
        bias = "neutral"
        metrics["anomaly_bias"] = 0.0
        conf = 0.50

    if stale:
        conf = max(0.20, conf - 0.15)
        notes.append("Volume indicators computed from cached data snapshot.")

    evidence.append(Evidence(
        source_type="price",
        source_id=f"volume:{ticker}:{last_date_str}",
        title=f"{ticker} Daily Volume & Turnover",
        snippet=f"Latest volume of {latest_volume:,} shares represented a {vol_ratio}x multiple over the 20-day mean (Z-Score: {z_score}) accompanied by a 1-day price move of {price_change_1d}%.",
        url=None,
        relevance=0.92
    ))

    prompt = (
        f"You are the Volume Anomaly Agent for {ticker}. Write 2 sentences explaining volume conditions: "
        f"Signal: {signal} (bias: {bias}), Volume Z-score: {z_score}, Ratio to 20d avg: {vol_ratio}x, 1-day price move: {price_change_1d}%. Strictly factual."
    )
    reasoning = gemini_client.generate(prompt)
    if not reasoning or "Deterministic" in reasoning or len(reasoning) < 20:
        if signal == "anomalous":
            reasoning = (
                f"{ticker} experienced an anomalous trading volume surge of {vol_ratio}x the 20-day average (z-score {z_score}), "
                f"coinciding with a 1-day price change of {price_change_1d}%, establishing a {bias} institutional participation bias."
            )
        else:
            reasoning = (
                f"Trading volume for {ticker} remains within normal historical statistical bounds at {vol_ratio}x the 20-day average "
                f"(z-score {z_score}), indicating no abnormal liquidity disruption."
            )

    return AgentOutput(
        agent="Volume Anomaly Agent",
        ticker=ticker,
        signal=signal,
        confidence=round(conf, 2),
        reasoning=reasoning.strip(),
        metrics=metrics,
        evidence=evidence,
        latency_ms=0,
        status="ok" if not stale else "degraded",
        notes=notes
    )

def run_volume_agent(ticker: str, df: pd.DataFrame, stale: bool = False) -> AgentOutput:
    return safe_run("Volume Anomaly Agent", ticker, _run_volume, ticker, df, stale)

