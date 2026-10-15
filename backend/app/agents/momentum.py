"""
backend/app/agents/momentum.py - Deterministic Momentum Signal Agent
"""

import pandas as pd
from backend.app.schemas.agent import AgentOutput, Evidence
from backend.app.features.indicators import compute_technical_features
from backend.app.agents.base import safe_run
from backend.app.llm.client import gemini_client

def _run_momentum(ticker: str, df: pd.DataFrame, stale: bool = False) -> AgentOutput:
    metrics = compute_technical_features(df)
    notes = []
    evidence = []

    rsi = metrics["rsi"]
    macd_hist = metrics["macd_hist"]
    macd_hist_rising = metrics["macd_hist_rising"]
    close = metrics["latest_close"]
    sma50 = metrics["sma50"]
    sma200 = metrics["sma200"]
    ret_20d = metrics["return_20d"]

    last_date_str = str(df['Date'].iloc[-1].strftime("%Y-%m-%d")) if not df.empty else "Recent"

    score = 0
    # Condition 1: RSI in 50-70 (+1) vs RSI < 50 (-1)
    if 50 <= rsi <= 70:
        score += 1
    elif rsi < 50:
        score -= 1
    
    if rsi > 75:
        notes.append(f"RSI {rsi} indicates overbought conditions; caution on chasing rallies.")
    elif rsi < 25:
        notes.append(f"RSI {rsi} indicates oversold conditions.")

    # Condition 2: MACD histogram > 0 and rising
    if macd_hist > 0 and macd_hist_rising:
        score += 1
    elif macd_hist < 0 and not macd_hist_rising:
        score -= 1

    # Condition 3: Moving average hierarchy close > SMA50 > SMA200
    if close > sma50 > sma200:
        score += 1
    elif close < sma50 < sma200:
        score -= 1

    # Condition 4: 20-day return > 0
    if ret_20d > 0:
        score += 1
    elif ret_20d < 0:
        score -= 1

    # Map score [-4, 4] to signal
    if score >= 2:
        signal = "bullish"
    elif score <= -2:
        signal = "bearish"
    else:
        signal = "neutral"

    # Confidence calculation
    conf = min(0.90, 0.40 + 0.12 * abs(score))
    if stale:
        conf = max(0.20, conf - 0.15)
        notes.append("Computed from stale snapshot pricing feed.")

    # Price-derived evidence citations
    evidence.append(Evidence(
        source_type="price",
        source_id=f"price:{ticker}:{last_date_str}:RSI",
        title=f"{ticker} Technical Price Feed",
        snippet=f"Closing price Rs {close} with 14-day RSI at {rsi} and 20-day cumulative return of {ret_20d}% as of {last_date_str}.",
        url=None,
        relevance=0.95
    ))

    evidence.append(Evidence(
        source_type="price",
        source_id=f"price:{ticker}:{last_date_str}:MA",
        title=f"{ticker} Moving Average Alignment",
        snippet=f"Price Rs {close} positioned relative to SMA50 (Rs {sma50}) and SMA200 (Rs {sma200}); MACD histogram at {macd_hist} ({'rising' if macd_hist_rising else 'falling'}).",
        url=None,
        relevance=0.90
    ))

    # LLM-written reasoning explanation
    prompt = (
        f"You are the Momentum Technical Agent for {ticker}. Explain the momentum stance in 2-3 sentences based strictly on these facts: "
        f"Score: {score}/4 ({signal}), RSI: {rsi}, Close: {close}, SMA50: {sma50}, SMA200: {sma200}, 20d return: {ret_20d}%. Do not invent facts."
    )
    reasoning = gemini_client.generate(prompt)
    if not reasoning or "Deterministic" in reasoning or len(reasoning) < 20:
        trend = "bullish trend alignment" if signal == "bullish" else ("bearish divergence" if signal == "bearish" else "consolidation")
        reasoning = (
            f"{ticker} is exhibiting a {trend} with a momentum score of {score}/4. "
            f"The 14-day RSI stands at {rsi} alongside a 20-day return of {ret_20d}%, while the price trades {'above' if close > sma50 else 'below'} "
            f"the 50-day moving average (Rs {sma50})."
        )

    return AgentOutput(
        agent="Momentum Agent",
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

def run_momentum_agent(ticker: str, df: pd.DataFrame, stale: bool = False) -> AgentOutput:
    return safe_run("Momentum Agent", ticker, _run_momentum, ticker, df, stale)

