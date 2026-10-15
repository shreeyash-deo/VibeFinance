"""
backend/app/agents/sentiment.py - Recency-Weighted News Sentiment Agent
"""

import math
from datetime import datetime
from backend.app.schemas.agent import AgentOutput, Evidence
from backend.app.agents.base import safe_run
from backend.app.llm.client import gemini_client

POSITIVE_WORDS = ["surge", "jump", "record", "profit", "raises", "growth", "high", "upgrade", "outperform", "gain", "deal", "win"]
NEGATIVE_WORDS = ["plunge", "fall", "slide", "drop", "cut", "warn", "slump", "loss", "probe", "pledge", "penalty", "observation", "risk", "pressure"]

def score_headline(title: str) -> float:
    t = title.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    if pos > neg:
        return 0.75
    elif neg > pos:
        return -0.75
    return 0.0

def _run_sentiment(ticker: str, headlines: list[dict], stale: bool = False) -> AgentOutput:
    notes = []
    evidence = []

    if not headlines:
        return AgentOutput(
            agent="Sentiment Agent",
            ticker=ticker,
            signal="no_data",
            confidence=0.0,
            reasoning=f"No recent news headlines available for {ticker} in the 14-day observation window.",
            metrics={"headline_count": 0.0, "sentiment_score": 0.0},
            evidence=[],
            latency_ms=0,
            status="degraded",
            notes=["No headlines located in news feed."]
        )

    # Recency-weighted aggregation (half-life of 5 days)
    # decay lambda = ln(2) / 5 ~= 0.1386
    lambda_decay = 0.1386
    total_weight = 0.0
    weighted_sum = 0.0
    scored_items = []

    now = datetime.utcnow()
    for item in headlines:
        pub_str = item.get("published_at", "")
        days_ago = 2.0
        try:
            pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00")).replace(tzinfo=None)
            days_ago = max(0.0, (now - pub_dt).total_seconds() / 86400.0)
        except Exception:
            pass

        score = item.get("sentiment_score")
        if score is None:
            # Check label or keyword score
            lbl = item.get("sentiment_label", "neutral")
            if lbl == "positive":
                score = 0.8
            elif lbl == "negative":
                score = -0.8
            else:
                score = score_headline(item.get("title", ""))

        w = math.exp(-lambda_decay * days_ago)
        weighted_sum += score * w
        total_weight += w
        scored_items.append((abs(score * w), score, item))

    aggregate_score = round(weighted_sum / total_weight, 3) if total_weight > 0 else 0.0

    # Determine Signal
    if aggregate_score > 0.20:
        signal = "bullish"
    elif aggregate_score < -0.20:
        signal = "bearish"
    else:
        signal = "neutral"

    # Confidence calculation: based on count & agreement
    n_headlines = len(headlines)
    base_conf = min(0.85, 0.40 + (n_headlines * 0.08))
    if n_headlines < 3:
        base_conf = 0.35
        notes.append("Low headline count (less than 3 items) reduces sentiment certainty.")

    if stale:
        base_conf = max(0.20, base_conf - 0.15)
        notes.append("Sentiment computed from cached snapshot headlines.")

    # Top 3 most influential headlines for evidence
    scored_items.sort(key=lambda x: x[0], reverse=True)
    top_items = scored_items[:3]
    for _, sc, item in top_items:
        evidence.append(Evidence(
            source_type="news",
            source_id=str(item.get("id", item.get("url", f"news:{ticker}"))),
            title=item.get("title", f"{ticker} News"),
            snippet=f"Publisher: {item.get('publisher', 'Financial Media')} | Sentiment: {'Positive' if sc > 0 else ('Negative' if sc < 0 else 'Neutral')} | Published: {item.get('published_at', 'Recent')}",
            url=item.get("url"),
            relevance=round(item.get("relevance", 0.85), 2)
        ))

    prompt = (
        f"You are the News Sentiment Agent for {ticker}. Summarize market sentiment in 2 sentences based on: "
        f"Weighted score: {aggregate_score} ({signal}), Headline count: {n_headlines}, Top headline: '{top_items[0][2].get('title') if top_items else 'N/A'}'. Do not hallucinate."
    )
    reasoning = gemini_client.generate(prompt)
    if not reasoning or "Deterministic" in reasoning or len(reasoning) < 20:
        tone = "predominantly positive" if signal == "bullish" else ("tilted negative" if signal == "bearish" else "broadly balanced")
        top_title = top_items[0][2].get("title", "") if top_items else "general market activity"
        reasoning = (
            f"Public news coverage across {n_headlines} verified financial headlines is {tone} with a recency-weighted score of {aggregate_score}. "
            f"Media discussions are anchored around '{top_title}'."
        )

    return AgentOutput(
        agent="Sentiment Agent",
        ticker=ticker,
        signal=signal,
        confidence=round(base_conf, 2),
        reasoning=reasoning.strip(),
        metrics={"sentiment_score": aggregate_score, "headline_count": float(n_headlines)},
        evidence=evidence,
        latency_ms=0,
        status="ok" if not stale else "degraded",
        notes=notes
    )

def run_sentiment_agent(ticker: str, headlines: list[dict], stale: bool = False) -> AgentOutput:
    return safe_run("Sentiment Agent", ticker, _run_sentiment, ticker, headlines, stale)

